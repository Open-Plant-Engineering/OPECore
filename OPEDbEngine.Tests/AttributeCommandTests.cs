using FluentAssertions;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Services.Claiming;
using Xunit;

public class AttributeCommandTests: IClassFixture<DbFixture>
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
        var claim = new ClaimService(db);
        var command = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session);

        var hash100 = await valueStore.StoreNumberAsync(100d);

        await claim.ClaimNodeAsync(nodeId, session);

        var v2 = await command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session);

        v2.Should().NotBe(v1);
    }

    [Fact]
    public async Task Should_Update_When_Node_Is_Claimed()
    {
        var db = CreateDb();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var claim = new ClaimService(db);
        var nodeService = new NodeService(db, attrSet);
        var command = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await claim.ClaimNodeAsync(nodeId, session);

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

    [Fact]
    public async Task Should_Reject_Without_Claim()
    {
        var db = CreateDb();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var claim = new ClaimService(db);
        var nodeService = new NodeService(db, attrSet);
        var command = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        var hash100 = await valueStore.StoreNumberAsync(100d);

        var act = async () => await command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");
    }

    [Fact]
    public async Task Should_Reject_When_Claimed_By_Other_Session()
    {
        var db = CreateDb();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var claim = new ClaimService(db);
        var nodeService = new NodeService(db, attrSet);
        var command = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var ownerSession = Guid.NewGuid();
        var otherSession = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", ownerSession);

        await claim.ClaimNodeAsync(nodeId, ownerSession);

        var hash100 = await valueStore.StoreNumberAsync(100d);

        var act = async () => await command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            otherSession);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");
    }

    [Fact]
    public async Task Should_Set_Multiple_Attributes()
    {
        var db = CreateDb();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var claim = new ClaimService(db);
        var nodeService = new NodeService(db, attrSet);
        var command = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await claim.ClaimNodeAsync(nodeId, session);

        var numHash = await valueStore.StoreNumberAsync(100d);
        var strHash = await valueStore.StoreStringAsync("CS");

        var v2 = await command.BulkSetAttributesAsync(
            nodeId,
            v1,
            new[]
            {
                new AttributeItem
                {
                    Key = 1,
                    ValueHash = numHash,
                    ValueType = 2
                },
                new AttributeItem
                {
                    Key = 2,
                    ValueHash = strHash,
                    ValueType = 1
                }
            },
            session);

        v2.Should().NotBe(v1);
    }

    [Fact]
    public async Task Should_Reject_Version_Mismatch()
    {
        var db = CreateDb();

        var hash = new HashService();
        var valueStore = new ValueStoreService(db, hash);
        var attrSet = new AttributeSetService();
        var version = new VersionService();
        var claim = new ClaimService(db);
        var nodeService = new NodeService(db, attrSet);
        var command = new AttributeCommandService(db, attrSet, version, claim);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await claim.ClaimNodeAsync(nodeId, session);

        var wrongVersion = Guid.NewGuid();

        var hash100 = await valueStore.StoreNumberAsync(100d);

        var act = async () => await command.SetAttributeAsync(
            nodeId,
            wrongVersion,
            1,
            hash100,
            2,
            session);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*Version mismatch*");
    }
}
