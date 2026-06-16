using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Claiming;
using Xunit;

public class SeedTests: IClassFixture<DbFixture>
{
    [Fact]
    public async Task Seed_Node_For_Grpc_Test()
    {
        var db = new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var nodeService = new NodeService(db, attrSet);
        var claim = new ClaimService(db);
        var cmd = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        var hash100 = await valueStore.StoreNumberAsync(100d);

        await claim.ClaimNodeAsync(nodeId, session); 
        
        var v2 = await cmd.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session);

        Console.WriteLine("USE THIS NODE ID:");
        Console.WriteLine(nodeId);
    }
}