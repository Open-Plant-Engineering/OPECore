using FluentAssertions;
using Xunit;
using SessionGrpc = OPEDbEngine.gRPC.Session;

public class SessionGrpcTests : GrpcTestBase
{
    [Fact]
    public async Task Should_Create_And_Close_Session()
    {
        var channel = CreateChannel();
        var client = new SessionGrpc.SessionService.SessionServiceClient(channel);

        // ✅ Start session
        var start = await client.StartSessionAsync(
            new SessionGrpc.StartSessionRequest
            {
                UserId = "atul"
            });

        start.SessionId.Should().NotBeNullOrEmpty();

        var sessionId = start.SessionId;

        // ✅ Close session
        var close = await client.CloseSessionAsync(
            new SessionGrpc.CloseSessionRequest
            {
                SessionId = sessionId
            });

        close.Should().NotBeNull();
        close.Success.Should().BeTrue();
        close.Message.Should().NotBeNullOrEmpty();
    }
}
