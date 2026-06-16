using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Nodes;
using Xunit;

public class NodeServiceTests : IClassFixture<DbFixture>
{
    private DbConnectionFactory CreateDb()
    {
        return new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");
    }

    // ✅ 1. Basic creation
    [Fact]
    public async Task Should_Create_Node_With_Initial_Version()
    {
        var db = CreateDb();

        var attrService = new AttributeSetService();
        var nodeService = new NodeService(db, attrService);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var version = await nodeService.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session);

        version.Should().NotBe(Guid.Empty);
    }

    // ✅ 2. Ensure DB pointer is correct
    [Fact]
    public async Task Should_Set_Current_Version_On_Node()
    {
        var db = CreateDb();

        var attrService = new AttributeSetService();
        var nodeService = new NodeService(db, attrService);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var versionId = await nodeService.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session);

        using var conn = db.Create();
        conn.Open();

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
        var db = CreateDb();

        var attrService = new AttributeSetService();
        var nodeService = new NodeService(db, attrService);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        var act = async () =>
            await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*already exists*");
    }

    // ✅ 4. Node must always have version
    [Fact]
    public async Task Node_Should_Always_Have_Version()
    {
        var db = CreateDb();

        var attrService = new AttributeSetService();
        var nodeService = new NodeService(db, attrService);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await nodeService.CreateNodeAsync(nodeId, "VALVE", "PIPING", session);

        using var conn = db.Create();
        conn.Open();

        var version = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT current_version_id FROM nodes WHERE id = @Id",
            new { Id = nodeId });

        version.Should().NotBeNull();
    }
}