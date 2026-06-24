using Dapper;
using FluentAssertions;
using Xunit;
using System.Data;

public class ClaimServiceTests
{
    private async Task<Guid> CreateSession(TestContext ctx, IDbConnection conn, IDbTransaction tx)
    {
        var userId = "test-user";

        await ctx.SessionRepo.EnsureUserExists(conn, userId, tx);

        return await ctx.Session.StartSessionAsync(userId, conn, tx);
    }

    // ✅ 1. Should claim node
    [Fact]
    public async Task Should_Claim_Node()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var sessionId = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, sessionId, conn, tx);

        tx.Commit();

        var claimed = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT claimed_by FROM node_claims WHERE node_id = @Id",
            new { Id = nodeId });

        claimed.Should().Be(sessionId);
    }

    // ✅ 2. Should reject duplicate claim
    [Fact]
    public async Task Should_Reject_When_Already_Claimed()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var session1 = await CreateSession(ctx, conn, tx);
        var session2 = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session1, conn, tx);

        var act = async () =>
            await ctx.Claim.ClaimNodeAsync(nodeId, session2, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*already claimed*");

        tx.Rollback();
    }

    // ✅ 3. Should validate correct claim
    [Fact]
    public async Task Should_Validate_Correct_Claim()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var sessionId = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, sessionId, conn, tx);

        var act = async () =>
            await ctx.Claim.ValidateClaimAsync(nodeId, sessionId, conn, tx);

        await act.Should().NotThrowAsync();

        tx.Commit();
    }

    // ✅ 4. Should reject wrong session
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

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, ownerSession, conn, tx);

        var act = async () =>
            await ctx.Claim.ValidateClaimAsync(nodeId, otherSession, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");

        tx.Rollback();
    }

    // ✅ 5. Should reject when no claim exists
    [Fact]
    public async Task Should_Reject_When_No_Claim_Exists()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var sessionId = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        var act = async () =>
            await ctx.Claim.ValidateClaimAsync(nodeId, sessionId, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");

        tx.Rollback();
    }

    // ✅ 6. Should release node
    [Fact]
    public async Task Should_Release_Node()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var sessionId = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, sessionId, conn, tx);
        await ctx.Claim.ReleaseNodeAsync(nodeId, sessionId, conn, tx);

        tx.Commit();

        var claim = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT claimed_by FROM node_claims WHERE node_id = @Id",
            new { Id = nodeId });

        claim.Should().BeNull();
    }

    // ✅ 7. Should reject release by non-owner
    [Fact]
    public async Task Should_Reject_Release_By_Other_User()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var owner = await CreateSession(ctx, conn, tx);
        var other = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, owner, conn, tx);

        var act = async () =>
            await ctx.Claim.ReleaseNodeAsync(nodeId, other, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not owner*");

        tx.Rollback();
    }

    // ✅ 8. Should force release
    [Fact]
    public async Task Should_Force_Release()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var owner = await CreateSession(ctx, conn, tx);
        var adminSession = await CreateSession(ctx, conn, tx);
        var nodeId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, owner, conn, tx);

        await ctx.Claim.ForceReleaseAsync(nodeId, adminSession, "admin cleanup", conn, tx);

        tx.Commit();

        var claim = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT claimed_by FROM node_claims WHERE node_id = @Id",
            new { Id = nodeId });

        claim.Should().BeNull();
    }
}