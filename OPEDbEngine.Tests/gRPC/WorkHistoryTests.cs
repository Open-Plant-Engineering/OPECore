using Xunit;
using FluentAssertions;
using System.Threading;

using WorkGrpc = OPEDbEngine.gRPC.Work;
using NodeGrpc = OPEDbEngine.gRPC.Node;
using SessionGrpc = OPEDbEngine.gRPC.Session;
using ClaimGrpc = OPEDbEngine.gRPC.Claim;

public class WorkHistoryTests : GrpcTestBase
{
    [Fact]
    public async Task Should_Stream_Node_History()
    {
        var channel = CreateChannel();

        var workClient = new WorkGrpc.WorkService.WorkServiceClient(channel);
        var nodeClient = new NodeGrpc.NodeService.NodeServiceClient(channel);
        var sessionClient = new SessionGrpc.SessionService.SessionServiceClient(channel);
        var claimClient = new ClaimGrpc.ClaimService.ClaimServiceClient(channel);

        var session = await sessionClient.StartSessionAsync(
            new SessionGrpc.StartSessionRequest { UserId = "atul" });

        var sessionId = session.SessionId;

        var nodeId = Guid.NewGuid().ToString();

        // ✅ create node
        var create = await nodeClient.CreateNodeAsync(new NodeGrpc.CreateNodeRequest
        {
            NodeId = nodeId,
            Type = "PIPE",
            Owner = "P",
            SessionId = sessionId
        });

        // ✅ claim
        using var claimCall = claimClient.StreamClaimNodes();

        await claimCall.RequestStream.WriteAsync(new ClaimGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        await claimCall.RequestStream.CompleteAsync();

        while (await claimCall.ResponseStream.MoveNext(CancellationToken.None)) { }

        // ✅ set attribute
        var value = await nodeClient.StoreValueAsync(
            new NodeGrpc.StoreValueRequest { NumberValue = 42 });

        await nodeClient.SetAttributeAsync(new NodeGrpc.SetAttributeRequest
        {
            NodeId = nodeId,
            VersionId = create.VersionId,
            Key = 1,
            ValueHash = value.ValueHash,
            ValueType = value.ValueType,
            SessionId = sessionId
        });

        // ✅ call history
        using var call = workClient.StreamNodeHistory(new WorkGrpc.NodeHistoryRequest
        {
            NodeId = nodeId
        });

        int count = 0;

        while (await call.ResponseStream.MoveNext(CancellationToken.None))
        {
            var res = call.ResponseStream.Current;
            res.NodeId.Should().Be(nodeId);
            count++;
        }

        count.Should().BeGreaterThan(0);
    }
}