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

public class QueryServiceTests : IClassFixture<DbFixture>
{
    private DbConnectionFactory Db() =>
        new DbConnectionFactory("Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

    // ✅ 1. Read latest value
    [Fact]
    public async Task Should_Read_Updated_Value()
    {
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "P", session);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        await ctx.Claim.ClaimNodeAsync(nodeId, session);

        var v2 = await ctx.Command.SetAttributeAsync(
            nodeId,
            v1,
            1,
            hash100,
            2,
            session);

        var result = await ctx.Query.GetNodeAsync(nodeId);

        result.NodeId.Should().Be(nodeId);
        result.VersionId.Should().Be(v2);

        result.Attributes.Should().ContainSingle(a =>
            a.Key == 1 &&
            (double)a.Value! == 100d);
    }

    // ✅ 2. Read old version
    [Fact]
    public async Task Should_Read_Old_Version_Data()
    {
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await ctx.Claim.ClaimNodeAsync(nodeId, session);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);
        var hash200 = await ctx.ValueStore.StoreNumberAsync(200d);

        var v2 = await ctx.Command.SetAttributeAsync(nodeId, v1, 1, hash100, 2, session);
        var v3 = await ctx.Command.SetAttributeAsync(nodeId, v2, 1, hash200, 2, session);

        var old = await ctx.Query.GetNodeVersionAsync(nodeId, v2);

        old.VersionId.Should().Be(v2);

        old.Attributes.Should().ContainSingle(a =>
            a.Key == 1 &&
            (double)a.Value! == 100d);
    }

    // ✅ 3. Multiple attributes read correctly
    [Fact]
    public async Task Should_Read_Multiple_Attributes()
    {
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await ctx.Claim.ClaimNodeAsync(nodeId, session);

        var numHash = await ctx.ValueStore.StoreNumberAsync(100d);
        var strHash = await ctx.ValueStore.StoreStringAsync("CS");

        var v2 = await ctx.Command.BulkSetAttributesAsync(
            nodeId,
            v1,
            new[]
            {
                new OPEDbEngine.Core.Models.AttributeItem
                {
                    Key = 1,
                    ValueHash = numHash,
                    ValueType = 2
                },
                new OPEDbEngine.Core.Models.AttributeItem
                {
                    Key = 2,
                    ValueHash = strHash,
                    ValueType = 1
                }
            },
            session);

        var result = await ctx.Query.GetNodeAsync(nodeId);

        result.Attributes.Should().HaveCount(2);

        result.Attributes.Should().Contain(a =>
            a.Key == 1 && (double)a.Value! == 100d);

        result.Attributes.Should().Contain(a =>
            a.Key == 2 && (string)a.Value! == "CS");
    }

    // ✅ 4. Node without attributes
    [Fact]
    public async Task Should_Return_Empty_Attributes_For_New_Node()
    {
        var db = Db();

        var attrSet = new AttributeSetService();
        var node = new NodeService(db, attrSet);
        var query = new QueryService(db);

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        var result = await query.GetNodeAsync(nodeId);

        result.Attributes.Should().BeEmpty();
    }
}