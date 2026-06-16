using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Claiming;
using Xunit;
using Dapper;

public class QueryServiceTests: IClassFixture<DbFixture>
{
    private DbConnectionFactory Db() =>
        new DbConnectionFactory("Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

    [Fact]
    public async Task Should_Read_Updated_Value()
    {
        var db = Db();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var node = new NodeService(db, attrSet);
        var claim = new ClaimService(db);
        var cmd = new AttributeCommandService(db, attrSet, version, claim);
        var query = new QueryService(db);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await node.CreateNodeAsync(nodeId, "PIPE", "P", session);

        Console.WriteLine($"v1: {v1}");

        var hash100 = await valueStore.StoreNumberAsync(100d);

        await claim.ClaimNodeAsync(nodeId, session); 
        
        var v2 = await cmd.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session);

        Console.WriteLine($"v2: {v2}");

        // ✅ DEBUG DB STATE
        using var conn = db.Create();

        var nodeRow = await conn.QueryFirstOrDefaultAsync<dynamic>(
            "SELECT id, current_version_id FROM nodes WHERE id = @Id",
            new { Id = nodeId });

        Console.WriteLine($"DB node current_version_id: {nodeRow?.current_version_id}");

        var versions = await conn.QueryAsync<dynamic>(
            "SELECT id, parent_version_id FROM versions WHERE node_id = @Id",
            new { Id = nodeId });

        foreach (var v in versions)
        {
            Console.WriteLine($"Version row: id={v.id}, parent={v.parent_version_id}");
        }

        var result = await query.GetNodeAsync(nodeId);

        result.Attributes.Should().ContainSingle(a =>
            a.Key == 1 &&
            (double)a.Value! == 100d);
    }
}