using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Nodes;
using Xunit;

public class NodeServiceTests: IClassFixture<DbFixture>
{
    private DbConnectionFactory CreateDb()
    {
        return new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");
    }

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
}