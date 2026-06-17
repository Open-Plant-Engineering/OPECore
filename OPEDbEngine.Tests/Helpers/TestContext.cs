using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Claiming;

public class TestContext
{
    public DbConnectionFactory Db { get; }
    public HashService Hash { get; }
    public ValueStoreService ValueStore { get; }
    public AttributeSetService AttributeSet { get; }
    public VersionService Version { get; }
    public NodeService Node { get; }
    public ClaimService Claim { get; }
    public AttributeCommandService Command { get; }
    public QueryService Query { get; }

    public TestContext()
    {
        Db = new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

        Hash = new HashService();
        ValueStore = new ValueStoreService(Db, Hash);
        AttributeSet = new AttributeSetService();
        Version = new VersionService();
        Node = new NodeService(Db, AttributeSet);
        Claim = new ClaimService(Db);

        // ✅ IMPORTANT: new dependency injected
        var AttributeRepo = new AttributeRepository();
        var NodeRepo = new NodeRepository();
        var VersionRepo = new VersionRepository();

        Command = new AttributeCommandService(Db, AttributeSet, Version, Claim, AttributeRepo, NodeRepo, VersionRepo);

        Query = new QueryService(Db);
    }
}