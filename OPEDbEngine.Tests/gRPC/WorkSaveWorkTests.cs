using Xunit;
using FluentAssertions;
using System.Threading;

using WorkGrpc = OPEDbEngine.gRPC.Work;
using ClaimGrpc = OPEDbEngine.gRPC.Claim;
using NodeGrpc = OPEDbEngine.gRPC.Node;
using SessionGrpc = OPEDbEngine.gRPC.Session;

public class WorkGrpcTests : GrpcTestBase
{
    [Fact]
    public async Task Should_Stream_Save_Changes()
    {
        var channel = CreateChannel();

        var workClient = new WorkGrpc.WorkService.WorkServiceClient(channel);
        var nodeClient = new NodeGrpc.NodeService.NodeServiceClient(channel);
        var sessionClient = new SessionGrpc.SessionService.SessionServiceClient(channel);

        var session = await sessionClient.StartSessionAsync(
            new SessionGrpc.StartSessionRequest { UserId = "atul" });

        var sessionId = session.SessionId;
        var nodeId = Guid.NewGuid().ToString();

        var claimClient = new ClaimGrpc.ClaimService.ClaimServiceClient(channel);

        // ✅ claim node before operations
        using var claimCall = claimClient.StreamClaimNodes();

        await claimCall.RequestStream.WriteAsync(new ClaimGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        await claimCall.RequestStream.CompleteAsync();

        // read claim response
        while (await claimCall.ResponseStream.MoveNext(CancellationToken.None)) { }

        using var call = workClient.StreamSaveChanges();

        // ✅ Create node
        await call.RequestStream.WriteAsync(new WorkGrpc.SaveNodeRequest
        {
            CreateNode = new NodeGrpc.CreateNodeRequest
            {
                NodeId = nodeId,
                Type = "PIPE",
                Owner = "P",
                SessionId = sessionId
            }
        });

        string versionId = "";

        if (await call.ResponseStream.MoveNext(CancellationToken.None))
        {
            var res = call.ResponseStream.Current;
            res.Success.Should().BeTrue();
            versionId = res.VersionId;
        }

        // ✅ Store value
        var value = await nodeClient.StoreValueAsync(
            new NodeGrpc.StoreValueRequest { NumberValue = 123 });

        // ✅ Set attribute
        await call.RequestStream.WriteAsync(new WorkGrpc.SaveNodeRequest
        {
            SetAttribute = new NodeGrpc.SetAttributeRequest
            {
                NodeId = nodeId,
                VersionId = versionId,
                Key = 1,
                ValueHash = value.ValueHash,
                ValueType = value.ValueType,
                SessionId = sessionId
            }
        });

        if (await call.ResponseStream.MoveNext(CancellationToken.None))
        {
            var res = call.ResponseStream.Current;
            res.Success.Should().BeTrue();
        }

        await call.RequestStream.CompleteAsync();
    }
}