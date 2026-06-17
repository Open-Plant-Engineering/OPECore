using FluentAssertions;
using Xunit;

public class QueryServiceTests : IClassFixture<DbFixture>
{
    [Fact]
    public async Task Should_Read_Updated_Value()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "P", session, conn, tx);

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

        using var readConn = ctx.Db.Create();
        readConn.Open();

        var result = await ctx.Query.GetNodeAsync(nodeId, readConn);

        result.NodeId.Should().Be(nodeId);
        result.VersionId.Should().Be(v2);

        result.Attributes.Should().ContainSingle(a =>
            a.Key == 1 &&
            (double)a.Value! == 100d);
    }

    [Fact]
    public async Task Should_Read_Old_Version_Data()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session, conn, tx);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);
        var hash200 = await ctx.ValueStore.StoreNumberAsync(200d);

        var v2 = await ctx.Command.SetAttributeAsync(nodeId, v1, 1, hash100, 2, session, conn, tx);
        var v3 = await ctx.Command.SetAttributeAsync(nodeId, v2, 1, hash200, 2, session, conn, tx);

        tx.Commit();

        using var readConn = ctx.Db.Create();
        readConn.Open();

        var old = await ctx.Query.GetNodeVersionAsync(nodeId, v2, readConn);

        old.VersionId.Should().Be(v2);

        old.Attributes.Should().ContainSingle(a =>
            a.Key == 1 &&
            (double)a.Value! == 100d);
    }

    [Fact]
    public async Task Should_Read_Multiple_Attributes()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session, conn, tx);

        await ctx.Claim.ClaimNodeAsync(nodeId, session, conn, tx);

        var numHash = await ctx.ValueStore.StoreNumberAsync(100d);
        var strHash = await ctx.ValueStore.StoreStringAsync("CS");

        var v2 = await ctx.Command.BulkSetAttributesAsync(
            nodeId,
            v1,
            new[]
            {
                new OPEDbEngine.Core.Models.AttributeItem
                {
                    Key = 1,
                    ValueHash = numHash,
                    ValueType = 2
                },
                new OPEDbEngine.Core.Models.AttributeItem
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

        using var readConn = ctx.Db.Create();
        readConn.Open();

        var result = await ctx.Query.GetNodeAsync(nodeId, readConn);

        result.Attributes.Should().HaveCount(2);

        result.Attributes.Should().Contain(a =>
            a.Key == 1 && (double)a.Value! == 100d);

        result.Attributes.Should().Contain(a =>
            a.Key == 2 && (string)a.Value! == "CS");
    }

    [Fact]
    public async Task Should_Return_Empty_Attributes_For_New_Node()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session, conn, tx);

        tx.Commit();

        using var readConn = ctx.Db.Create();
        readConn.Open();

        var result = await ctx.Query.GetNodeAsync(nodeId, readConn);

        result.Attributes.Should().BeEmpty();
    }
}