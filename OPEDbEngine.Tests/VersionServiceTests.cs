using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Versioning;
using Xunit;

public class VersionServiceTests
{
    private DbConnectionFactory CreateDb()
    {
        return new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");
    }

    [Fact]
    public async Task Should_Create_New_Version()
    {
        var db = CreateDb();
        var service = new VersionService();

        using var conn = db.Create();
        conn.Open();

        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var versionId = Guid.NewGuid();
        var attrSet = Guid.NewGuid();
        var session = Guid.NewGuid();

        // ✅ insert node
        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner, current_version_id) VALUES (@Id,'PIPE','P',@V)",
            new { Id = nodeId, V = versionId },
            tx);

        // ✅ insert initial version
        await conn.ExecuteAsync(
            @"INSERT INTO versions
              (id, node_id, parent_version_id, attribute_set_id, created_by)
              VALUES (@Id, @NodeId, NULL, @Attr, @Session)",
            new
            {
                Id = versionId,
                NodeId = nodeId,
                Attr = attrSet,
                Session = session
            },
            tx);

        var newSet = Guid.NewGuid();

        var newVersion = await service.CreateVersionAsync(
            nodeId,
            versionId,
            newSet,
            session,
            conn,
            tx);

        newVersion.Should().NotBe(versionId);

        tx.Commit();
    }
}