using FluentAssertions;
using Grpc.Net.Client;
using OPEDbEngine.Api;
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

        var client = new OPEDbEngine.Api.NodeService.NodeServiceClient(channel);

        var nodeId = Guid.NewGuid().ToString();
        var sessionId = Guid.NewGuid().ToString();

        // ✅ 1. Create Node
        var createResponse = await client.CreateNodeAsync(new CreateNodeRequest
        {
            NodeId = nodeId,
            Type = "PIPE",
            Owner = "P",
            SessionId = sessionId
        });

        createResponse.VersionId.Should().NotBeNullOrEmpty();

        var v1 = createResponse.VersionId;

        // ✅ 2. Claim Node
        var claimResponse = await client.ClaimNodeAsync(new ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        claimResponse.Success.Should().BeTrue();

        // ✅ 3. (IMPORTANT) Generate valueHash
        // Temporary manual hash for demo (must come from ValueStore API ideally)
        var storeResponse = await client.StoreValueAsync(new StoreValueRequest
        {
            NumberValue = 100
        });

        var setResponse = await client.SetAttributeAsync(new SetAttributeRequest
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
        var node = await client.GetNodeAsync(new GetNodeRequest
        {
            NodeId = nodeId
        });

        node.NodeId.Should().Be(nodeId);
        node.VersionId.Should().Be(v2);
        node.Attributes.Should().Contain(a =>
            a.Key == 1 &&
            a.Value == "100");

        var removeResponse = await client.RemoveAttributeAsync(new RemoveAttributeRequest
        {
            NodeId = nodeId,
            VersionId = v2,
            Key = 1,
            SessionId = sessionId
        });
        
        var nodeAfterRemove = await client.GetNodeAsync(new GetNodeRequest
        {
            NodeId = nodeId
        });
        
        nodeAfterRemove.Attributes.Should().BeEmpty();
        
    }
}