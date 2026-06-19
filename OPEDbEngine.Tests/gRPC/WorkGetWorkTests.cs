using Xunit;
using FluentAssertions;
using System.Threading;

using WorkGrpc = OPEDbEngine.gRPC.Work;
using NodeGrpc = OPEDbEngine.gRPC.Node;
using SessionGrpc = OPEDbEngine.gRPC.Session;
using ClaimGrpc = OPEDbEngine.gRPC.Claim;

public class WorkGetWorkTests : GrpcTestBase
{
    [Fact]
    public async Task Should_Get_Latest_Node_State()
    {
        var channel = CreateChannel();

        var workClient = new WorkGrpc.WorkService.WorkServiceClient(channel);
        var nodeClient = new NodeGrpc.NodeService.NodeServiceClient(channel);
        var sessionClient = new SessionGrpc.SessionService.SessionServiceClient(channel);
        var claimClient = new ClaimGrpc.ClaimService.ClaimServiceClient(channel);

        // ✅ Start session
        var session = await sessionClient.StartSessionAsync(
            new SessionGrpc.StartSessionRequest { UserId = "atul" });

        var sessionId = session.SessionId;

        // ✅ Create node
        var nodeId = Guid.NewGuid().ToString();

        var create = await nodeClient.CreateNodeAsync(new NodeGrpc.CreateNodeRequest
        {
            NodeId = nodeId,
            Type = "PIPE",
            Owner = "P",
            SessionId = sessionId
        });

        // ✅ Claim node (required for modification)
        using var claimCall = claimClient.StreamClaimNodes();

        await claimCall.RequestStream.WriteAsync(new ClaimGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        await claimCall.RequestStream.CompleteAsync();

        while (await claimCall.ResponseStream.MoveNext(CancellationToken.None)) { }

        // ✅ Store value
        var value = await nodeClient.StoreValueAsync(
            new NodeGrpc.StoreValueRequest { StringValue = "TEST" });

        // ✅ Set attribute
        await nodeClient.SetAttributeAsync(new NodeGrpc.SetAttributeRequest
        {
            NodeId = nodeId,
            VersionId = create.VersionId,
            Key = 1,
            ValueHash = value.ValueHash,
            ValueType = value.ValueType,
            SessionId = sessionId
        });

        // ✅ CALL GET WORK
        using var call = workClient.StreamGetWork(new WorkGrpc.GetWorkRequest
        {
            NodeId = nodeId
        });

        WorkGrpc.GetWorkResponse response = null;

        if (await call.ResponseStream.MoveNext(CancellationToken.None))
        {
            response = call.ResponseStream.Current;
        }

        response.Should().NotBeNull();
        response.NodeId.Should().Be(nodeId);
        response.Attributes.Should().Contain(a => a.Key == 1);
    }
}
