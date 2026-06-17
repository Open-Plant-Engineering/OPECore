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
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(
            nodeId,
            "PIPE",
            "PIPING",
            session);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        await ctx.Claim.ClaimNodeAsync(nodeId, session);

        var v2 = await ctx.Command.SetAttributeAsync(
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
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await ctx.Claim.ClaimNodeAsync(nodeId, session);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var v2 = await ctx.Command.SetAttributeAsync(
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
        var ctx = new TestContext();
        
        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var act = async () => await ctx.Command.SetAttributeAsync(
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
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var ownerSession = Guid.NewGuid();
        var otherSession = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", ownerSession);

        await ctx.Claim.ClaimNodeAsync(nodeId, ownerSession);

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var act = async () => await ctx.Command.SetAttributeAsync(
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
        var ctx = new TestContext();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        var v1 = await ctx.Node.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

        await ctx.Claim.ClaimNodeAsync(nodeId, session);

        var wrongVersion = Guid.NewGuid();

        var hash100 = await ctx.ValueStore.StoreNumberAsync(100d);

        var act = async () => await ctx.Command.SetAttributeAsync(
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
