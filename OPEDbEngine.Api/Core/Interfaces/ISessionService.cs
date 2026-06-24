using System.Data;

public interface ISessionService
{
    Task<Guid> StartSessionAsync(string userId, IDbConnection conn, IDbTransaction tx);
    Task CloseSessionAsync(Guid sessionId, IDbConnection conn, IDbTransaction tx);
}
