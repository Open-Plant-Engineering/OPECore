using FluentAssertions;
using Grpc.Net.Client;
using SessionGrpc = OPEDbEngine.gRPC.session;
using SessionDomain = OPEDbEngine.Infrastructure.Services;
using NodeGrpc = OPEDbEngine.gRPC.Node;
using Xunit;

public class GrpcClientTests
{
    private static GrpcChannel CreateChannel()
    {
        return GrpcChannel.ForAddress("http://localhost:5217");
    }

    [Fact]
    public async Task Full_EndToEnd_gRPC_Test()
    {
        using var channel = CreateChannel();

        var client = new NodeGrpc.NodeService.NodeServiceClient(channel);

        var nodeId = Guid.NewGuid().ToString();
        var sessionId = Guid.NewGuid().ToString();

        // ✅ 1. Create Node
        var createResponse = await client.CreateNodeAsync(new NodeGrpc.CreateNodeRequest
        {
            NodeId = nodeId,
            Type = "PIPE",
            Owner = "P",
            SessionId = sessionId
        });

        createResponse.VersionId.Should().NotBeNullOrEmpty();

        var v1 = createResponse.VersionId;

        // ✅ 2. Claim Node
        var claimResponse = await client.ClaimNodeAsync(new NodeGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        claimResponse.Success.Should().BeTrue();

        // ✅ 3. (IMPORTANT) Generate valueHash
        // Temporary manual hash for demo (must come from ValueStore API ideally)
        var storeResponse = await client.StoreValueAsync(new NodeGrpc.StoreValueRequest
        {
            NumberValue = 100
        });

        var setResponse = await client.SetAttributeAsync(new NodeGrpc.SetAttributeRequest
        {
            NodeId = nodeId,
            VersionId = v1,
            Key = 1,
            ValueHash = storeResponse.ValueHash,
            ValueType = storeResponse.ValueType,
            SessionId = sessionId
        });

        setResponse.NewVersionId.Should().NotBeNullOrEmpty();

        var v2 = setResponse.NewVersionId;

        // ✅ 4. Get Node
        var node = await client.GetNodeAsync(new NodeGrpc.GetNodeRequest
        {
            NodeId = nodeId
        });

        node.NodeId.Should().Be(nodeId);
        node.VersionId.Should().Be(v2);
        node.Attributes.Should().Contain(a =>
            a.Key == 1 &&
            a.Value == "100");

        var removeResponse = await client.RemoveAttributeAsync(new NodeGrpc.RemoveAttributeRequest
        {
            NodeId = nodeId,
            VersionId = v2,
            Key = 1,
            SessionId = sessionId
        });
        
        var nodeAfterRemove = await client.GetNodeAsync(new NodeGrpc.GetNodeRequest
        {
            NodeId = nodeId
        });
        
        nodeAfterRemove.Attributes.Should().BeEmpty();   
    }

    [Fact]
    public async Task Should_Bulk_Set_Attributes()
    {
        using var channel = GrpcChannel.ForAddress("http://localhost:5217");
        var client = new NodeGrpc.NodeService.NodeServiceClient(channel);

        var nodeId = Guid.NewGuid().ToString();
        var session = Guid.NewGuid().ToString();

        var v1 = (await client.CreateNodeAsync(new NodeGrpc.CreateNodeRequest
        {
            NodeId = nodeId,
            Type = "PIPE",
            Owner = "P",
            SessionId = session
        })).VersionId;

        await client.ClaimNodeAsync(new NodeGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = session
        });

        var v100 = await client.StoreValueAsync(new NodeGrpc.StoreValueRequest { NumberValue = 100 });
        var v200 = await client.StoreValueAsync(new NodeGrpc.StoreValueRequest { NumberValue = 200 });

        var res = await client.BulkSetAttributesAsync(new NodeGrpc.BulkSetAttributesRequest
        {
            NodeId = nodeId,
            VersionId = v1,
            SessionId = session,
            Attributes =
            {
                new NodeGrpc.AttributeWrite { Key = 1, ValueHash = v100.ValueHash, ValueType = v100.ValueType },
                new NodeGrpc.AttributeWrite { Key = 2, ValueHash = v200.ValueHash, ValueType = v200.ValueType }
            }
        });

        var node = await client.GetNodeAsync(new NodeGrpc.GetNodeRequest { NodeId = nodeId });

        node.Attributes.Should().HaveCount(2);
    }
    
}