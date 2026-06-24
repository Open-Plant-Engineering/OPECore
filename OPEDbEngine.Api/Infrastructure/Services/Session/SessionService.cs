using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;

public class SessionService : ISessionService
{
    private readonly SessionRepository _repo;

    public SessionService(SessionRepository repo)
    {
        _repo = repo;
    }

    public async Task<Guid> StartSessionAsync(
        string userId,
        IDbConnection conn,
        IDbTransaction tx)
    {
        // ✅ ensure user exists
        var exists = await _repo.UserExists(conn, userId, tx);

        if (!exists)
            throw new InvalidOperationException("User does not exist.");
    
        var sessionId = Guid.NewGuid();
    
        await _repo.InsertSession(conn, sessionId, userId, tx);
    
        return sessionId;
    }


    public async Task CloseSessionAsync(
        Guid sessionId,
        IDbConnection conn,
        IDbTransaction tx)
    {
        await _repo.DeleteSession(conn, sessionId, tx);
    }

    public async Task AbortSessionAsync(
        Guid sessionId,
        string reason,
        IDbConnection conn,
        IDbTransaction tx)
    {
        // optional: add audit log later

        await _repo.DeleteSession(conn, sessionId, tx);
    }
}