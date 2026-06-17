using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Claiming;
using OPEDbEngine.Infrastructure.Services.Hashing;

public class TestContext
{
    public DbConnectionFactory Db { get; }

    public HashService Hash { get; }
    public ValueStoreService ValueStore { get; }

    public AttributeRepository AttributeRepo { get; }
    public NodeRepository NodeRepo { get; }
    public VersionRepository VersionRepo { get; }
    public ClaimRepository ClaimRepo { get; }
    public ValueRepository ValueRepo { get; }

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

        // ✅ Infra
        Hash = new HashService();

        // ✅ Repositories
        AttributeRepo = new AttributeRepository();
        NodeRepo = new NodeRepository();
        VersionRepo = new VersionRepository();
        ClaimRepo = new ClaimRepository();
        ValueRepo = new ValueRepository();

        ValueStore = new ValueStoreService(Db, Hash, ValueRepo);

        // Services
        AttributeSet = new AttributeSetService(AttributeRepo);
        Version = new VersionService(VersionRepo);
        Node = new NodeService(Db, AttributeSet, NodeRepo, VersionRepo);
        Claim = new ClaimService(Db, ClaimRepo);

        Command = new AttributeCommandService(
            Db,
            AttributeSet,
            Version,
            Claim,
            AttributeRepo,
            NodeRepo,
            VersionRepo);

        Query = new QueryService(
            Db,
            NodeRepo,
            VersionRepo,
            AttributeRepo,
            ValueRepo);
    }
}