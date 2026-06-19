using Xunit;
using FluentAssertions;
using System.Threading;

using ClaimGrpc = OPEDbEngine.gRPC.Claim;
using SessionGrpc = OPEDbEngine.gRPC.Session;
using NodeGrpc = OPEDbEngine.gRPC.Node;

public class ClaimGrpcTests : GrpcTestBase
{
    [Fact]
    public async Task Should_Claim_And_Release_Multiple_Nodes_Stream()
    {
        var channel = CreateChannel();

        var claimClient = new ClaimGrpc.ClaimService.ClaimServiceClient(channel);
        var sessionClient = new SessionGrpc.SessionService.SessionServiceClient(channel);
        var nodeClient = new NodeGrpc.NodeService.NodeServiceClient(channel);

        // ✅ 1. Create session
        var session = await sessionClient.StartSessionAsync(
            new SessionGrpc.StartSessionRequest
            {
                UserId = "atul"
            });

        var sessionId = session.SessionId;

        // ✅ 2. Create nodes
        var nodeIds = new List<string>();

        for (int i = 0; i < 3; i++)
        {
            var nodeId = Guid.NewGuid().ToString();

            await nodeClient.CreateNodeAsync(new NodeGrpc.CreateNodeRequest
            {
                NodeId = nodeId,
                Type = "PIPE",
                Owner = "P",
                SessionId = sessionId
            });

            nodeIds.Add(nodeId);
        }

        // ✅ 3. STREAM CLAIM
        using var claimCall = claimClient.StreamClaimNodes();

        foreach (var nodeId in nodeIds)
        {
            await claimCall.RequestStream.WriteAsync(
                new ClaimGrpc.ClaimNodeRequest
                {
                    NodeId = nodeId,
                    SessionId = sessionId
                });
        }

        await claimCall.RequestStream.CompleteAsync();

        var claimResults = new List<ClaimGrpc.ClaimNodeResponse>();

        while (await claimCall.ResponseStream.MoveNext(CancellationToken.None))
        {
            claimResults.Add(claimCall.ResponseStream.Current);
        }

        claimResults.Should().HaveCount(3);
        claimResults.Should().OnlyContain(r => r.Success);

        // ✅ 4. STREAM RELEASE
        using var releaseCall = claimClient.StreamReleaseNodes();

        foreach (var nodeId in nodeIds)
        {
            await releaseCall.RequestStream.WriteAsync(
                new ClaimGrpc.ReleaseNodeRequest
                {
                    NodeId = nodeId,
                    SessionId = sessionId
                });
        }

        await releaseCall.RequestStream.CompleteAsync();

        var releaseResults = new List<ClaimGrpc.ReleaseNodeResponse>();

        while (await releaseCall.ResponseStream.MoveNext(CancellationToken.None))
        {
            releaseResults.Add(releaseCall.ResponseStream.Current);
        }

        releaseResults.Should().HaveCount(3);
        releaseResults.Should().OnlyContain(r => r.Success);
    }

    [Fact]
    public async Task Should_Fail_When_Claiming_Already_Claimed_Node()
    {
        var channel = CreateChannel();

        var claimClient = new ClaimGrpc.ClaimService.ClaimServiceClient(channel);
        var sessionClient = new SessionGrpc.SessionService.SessionServiceClient(channel);
        var nodeClient = new NodeGrpc.NodeService.NodeServiceClient(channel);

        var session = await sessionClient.StartSessionAsync(
            new SessionGrpc.StartSessionRequest
            {
                UserId = "atul"
            });

        var sessionId = session.SessionId;

        var nodeId = Guid.NewGuid().ToString();

        await nodeClient.CreateNodeAsync(new NodeGrpc.CreateNodeRequest
        {
            NodeId = nodeId,
            Type = "PIPE",
            Owner = "P",
            SessionId = sessionId
        });

        // ✅ First claim
        using var firstCall = claimClient.StreamClaimNodes();

        await firstCall.RequestStream.WriteAsync(new ClaimGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        await firstCall.RequestStream.CompleteAsync();

        while (await firstCall.ResponseStream.MoveNext(CancellationToken.None)) { }

        // ✅ Second claim (should fail)
        using var secondCall = claimClient.StreamClaimNodes();

        await secondCall.RequestStream.WriteAsync(new ClaimGrpc.ClaimNodeRequest
        {
            NodeId = nodeId,
            SessionId = sessionId
        });

        await secondCall.RequestStream.CompleteAsync();

        var responses = new List<ClaimGrpc.ClaimNodeResponse>();

        while (await secondCall.ResponseStream.MoveNext(CancellationToken.None))
        {
            responses.Add(secondCall.ResponseStream.Current);
        }

        responses.Should().HaveCount(1);
        responses[0].Success.Should().BeFalse();
    }
}