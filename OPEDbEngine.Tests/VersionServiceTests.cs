using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Versioning;
using Xunit;

public class VersionServiceTests : IClassFixture<DbFixture>
{
    private DbConnectionFactory CreateDb()
    {
        return new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");
    }

    // ✅ 1. Should create new version
    [Fact]
    public async Task Should_Create_New_Version()
    {
        var db = CreateDb();
        var service = new VersionService();

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var v1 = Guid.NewGuid();
        var attrSet = Guid.NewGuid();
        var session = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner, current_version_id) VALUES (@Id,'PIPE','P',@V)",
            new { Id = nodeId, V = v1 }, tx);

        await conn.ExecuteAsync(
            @"INSERT INTO versions
              (id, node_id, parent_version_id, attribute_set_id, created_by)
              VALUES (@Id, @NodeId, NULL, @Attr, @Session)",
            new { Id = v1, NodeId = nodeId, Attr = attrSet, Session = session }, tx);

        var newSet = Guid.NewGuid();

        var v2 = await service.CreateVersionAsync(
            nodeId,
            v1,
            newSet,
            session,
            conn,
            tx);

        v2.Should().NotBe(v1);

        tx.Commit();
    }

    // ✅ 2. Reject version mismatch
    [Fact]
    public async Task Should_Reject_On_Version_Mismatch()
    {
        var db = CreateDb();
        var service = new VersionService();

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var v1 = Guid.NewGuid();
        var attrSet = Guid.NewGuid();
        var session = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner, current_version_id) VALUES (@Id,'PIPE','P',@V)",
            new { Id = nodeId, V = v1 }, tx);

        await conn.ExecuteAsync(
            @"INSERT INTO versions
              (id, node_id, parent_version_id, attribute_set_id, created_by)
              VALUES (@Id, @NodeId, NULL, @Attr, @Session)",
            new { Id = v1, NodeId = nodeId, Attr = attrSet, Session = session }, tx);

        var wrongVersion = Guid.NewGuid();

        var act = async () => await service.CreateVersionAsync(
            nodeId,
            wrongVersion,
            attrSet,
            session,
            conn,
            tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*Version mismatch*");

        tx.Rollback();
    }

    // ✅ 3. Reject stale update (OCC check)
    [Fact]
    public async Task Should_Reject_Second_Update_With_Same_Version()
    {
        var db = CreateDb();
        var service = new VersionService();

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var v1 = Guid.NewGuid();
        var attrSet = Guid.NewGuid();
        var session = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner, current_version_id) VALUES (@Id,'PIPE','P',@V)",
            new { Id = nodeId, V = v1 }, tx);

        await conn.ExecuteAsync(
            @"INSERT INTO versions
              (id, node_id, parent_version_id, attribute_set_id, created_by)
              VALUES (@Id, @NodeId, NULL, @Attr, @Session)",
            new { Id = v1, NodeId = nodeId, Attr = attrSet, Session = session }, tx);

        // ✅ first update
        var v2 = await service.CreateVersionAsync(nodeId, v1, attrSet, session, conn, tx);

        // ❌ stale retry using v1
        var act = async () => await service.CreateVersionAsync(
            nodeId,
            v1,
            attrSet,
            session,
            conn,
            tx);

        await act.Should().ThrowAsync<InvalidOperationException>();

        tx.Rollback();
    }

    // ✅ 4. Reject when node does not exist
    [Fact]
    public async Task Should_Reject_When_Node_Does_Not_Exist()
    {
        var db = CreateDb();
        var service = new VersionService();

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var fakeNode = Guid.NewGuid();
        var attrSet = Guid.NewGuid();
        var session = Guid.NewGuid();

        var act = async () => await service.CreateVersionAsync(
            fakeNode,
            Guid.Empty,
            attrSet,
            session,
            conn,
            tx);

        await act.Should().ThrowAsync<InvalidOperationException>();

        tx.Rollback();
    }

    // ✅ 5. Verify version chain correctness
    [Fact]
    public async Task Should_Create_Proper_Version_Chain()
    {
        var db = CreateDb();
        var service = new VersionService();

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var v1 = Guid.NewGuid();
        var attrSet = Guid.NewGuid();
        var session = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner, current_version_id) VALUES (@Id,'PIPE','P',@V)",
            new { Id = nodeId, V = v1 }, tx);

        await conn.ExecuteAsync(
            @"INSERT INTO versions
              (id, node_id, parent_version_id, attribute_set_id, created_by)
              VALUES (@Id, @NodeId, NULL, @Attr, @Session)",
            new { Id = v1, NodeId = nodeId, Attr = attrSet, Session = session }, tx);

        var v2 = await service.CreateVersionAsync(nodeId, v1, attrSet, session, conn, tx);

        var parent = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT parent_version_id FROM versions WHERE id = @Id",
            new { Id = v2 }, tx);

        parent.Should().Be(v1);

        tx.Commit();
    }
}