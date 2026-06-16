using FluentAssertions;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Hashing;
using Xunit;

public class AttributeCommandTests
{
    private DbConnectionFactory CreateDb()
    {
        return new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");
    }

    [Fact]
    public async Task Should_Update_Attribute_And_Create_New_Version()
    {
        var db = CreateDb();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var nodeService = new NodeService(db, attrSet);
        var command = new AttributeCommandService(db, attrSet, version);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session);

        var hash100 = await valueStore.StoreNumberAsync(100d);

        var v2 = await command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session);

        v2.Should().NotBe(v1);
    }
}
