using Dapper;
using FluentAssertions;
using Xunit;

public class NodeServiceTests : IClassFixture<DbFixture>
{
    // ✅ 1. Basic creation
    [Fact]
    public async Task Should_Create_Node_With_Initial_Version()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var version = await ctx.Node.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session,
            conn,
            tx);

        tx.Commit();

        version.Should().NotBe(Guid.Empty);
    }

    // ✅ 2. Ensure DB pointer is correct
    [Fact]
    public async Task Should_Set_Current_Version_On_Node()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var versionId = await ctx.Node.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session,
            conn,
            tx);

        tx.Commit(); // ✅ commit before query

        var dbVersion = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT current_version_id FROM nodes WHERE id = @Id",
            new { Id = nodeId });

        dbVersion.Should().NotBeNull();
        dbVersion.Should().Be(versionId);
    }

    // ✅ 3. Reject duplicate node creation
    [Fact]
    public async Task Should_Reject_Duplicate_Node()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session, conn, tx);

        var act = async () =>
            await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*already exists*");

        tx.Rollback();
    }

    // ✅ 4. Node must always have version
    [Fact]
    public async Task Node_Should_Always_Have_Version()
    {
        var ctx = new TestContext();

        using var conn = ctx.Db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await ctx.Node.CreateNodeAsync(nodeId, "VALVE", "PIPING", session, conn, tx);

        tx.Commit();

        var version = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT current_version_id FROM nodes WHERE id = @Id",
            new { Id = nodeId });

        version.Should().NotBeNull();
    }
}