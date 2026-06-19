using Grpc.Core;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using SessionGrpc = OPEDbEngine.gRPC.Session;
using SessionDomain = OPEDbEngine.Infrastructure.Services;

public class SessionGrpcService : SessionGrpc.SessionService.SessionServiceBase
{
    private readonly ISessionService _service;
    private readonly DbConnectionFactory _db;

    public SessionGrpcService(ISessionService service, DbConnectionFactory db)
    {
        _service = service;
        _db = db;
    }

    public override async Task<SessionGrpc.StartSessionResponse> StartSession(
        SessionGrpc.StartSessionRequest request,
        ServerCallContext context)
    {
        using var conn = _db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var sessionId = await _service.StartSessionAsync(
            request.UserId,
            conn,
            tx);

        tx.Commit();

        return new SessionGrpc.StartSessionResponse
        {
            SessionId = sessionId.ToString()
        };
    }

    public override async Task<SessionGrpc.EmptyResponse> CloseSession(
        SessionGrpc.CloseSessionRequest request,
        ServerCallContext context)
    {
        using var conn = _db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        await _service.CloseSessionAsync(
            Guid.Parse(request.SessionId),
            conn,
            tx);

        tx.Commit();

        return new SessionGrpc.EmptyResponse();
    }

    public override async Task<SessionGrpc.EmptyResponse> AbortSession(
        SessionGrpc.AbortSessionRequest request,
        ServerCallContext context)
    {
        using var conn = _db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        await _service.AbortSessionAsync(
            Guid.Parse(request.SessionId),
            request.Reason,
            conn,
            tx);

        tx.Commit();

        return new SessionGrpc.EmptyResponse();
    }
}