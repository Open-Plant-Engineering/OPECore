using FluentAssertions;
using OPEDbEngine.Core.Models;
using Xunit;
using System.Data;

public class AttributeCommandTests
{
    private async Task<Guid> CreateSession(TestContext ctx, IDbConnection conn, IDbTransaction tx)
    {
        var userId = "test-user";

        await ctx.SessionRepo.EnsureUserExists(conn, userId, tx);

        return await ctx.Session.StartSessionAsync(userId, conn, tx);
    }

    [Fact]
    public async Task Should_Update_Attribute_And_Create_New_Version()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var session = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(
            nodeId, "PIPE", "PIPING", session, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session, conn, tx);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var v2 = await ctx.Command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session,
            conn,
            tx);

        tx.Commit();

        v2.Should().NotBe(v1);
    }

    [Fact]
    public async Task Should_Update_When_Node_Is_Claimed()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var session = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(
            nodeId, "PIPE", "PIPING", session, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session, conn, tx);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var v2 = await ctx.Command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session,
            conn,
            tx);

        tx.Commit();

        v2.Should().NotBe(v1);
    }

    [Fact]
    public async Task Should_Reject_Without_Claim()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var session = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(
            nodeId, "PIPE", "PIPING", session, conn, tx);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var act = async () =>
            await ctx.Command.SetAttributeAsync(
                nodeId,
                v1,
                1,
                hash100,
                2,
                session,
                conn,
                tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");

        tx.Rollback();
    }

    [Fact]
    public async Task Should_Reject_When_Claimed_By_Other_Session()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var ownerSession = await CreateSession(ctx, conn, tx);
        var otherSession = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(
            nodeId, "PIPE", "PIPING", ownerSession, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, ownerSession, conn, tx);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var act = async () =>
            await ctx.Command.SetAttributeAsync(
                nodeId,
                v1,
                1,
                hash100,
                2,
                otherSession,
                conn,
                tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");

        tx.Rollback();
    }

    [Fact]
    public async Task Should_Set_Multiple_Attributes()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var session = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(
            nodeId, "PIPE", "PIPING", session, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session, conn, tx);

        var numHash = await ctx.ValueStore.StoreNumberAsync(100d);
        var strHash = await ctx.ValueStore.StoreStringAsync("CS");

        var v2 = await ctx.Command.BulkSetAttributesAsync(
            nodeId,
            v1,
            new[]
            {
                new AttributeItem
                {
                    Key = 1,
                    ValueHash = numHash,
                    ValueType = 2
                },
                new AttributeItem
                {
                    Key = 2,
                    ValueHash = strHash,
                    ValueType = 1
                }
            },
            session,
            conn,
            tx);

        tx.Commit();

        v2.Should().NotBe(v1);
    }

    [Fact]
    public async Task Should_Reject_Version_Mismatch()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var session = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        var wrongVersion = Guid.NewGuid();

        await ctx.Node.CreateNodeAsync(
            nodeId, "PIPE", "PIPING", session, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session, conn, tx);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var act = async () =>
            await ctx.Command.SetAttributeAsync(
                nodeId,
                wrongVersion,
                1,
                hash100,
                2,
                session,
                conn,
                tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*Version mismatch*");

        tx.Rollback();
    }
}
