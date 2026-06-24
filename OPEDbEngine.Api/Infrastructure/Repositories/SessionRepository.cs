using Dapper;
using System.Data;

public class SessionRepository
{
    public async Task InsertSession(
        IDbConnection conn,
        Guid sessionId,
        string userId,
        IDbTransaction tx)
    {
        await conn.ExecuteAsync(
            @"INSERT INTO sessions (id, user_id)
              VALUES (@Id, @User)",
            new { Id = sessionId, User = userId },
            tx);
    }

    public async Task DeleteSession(
        IDbConnection conn,
        Guid sessionId,
        IDbTransaction tx)
    {
        await conn.ExecuteAsync(
            "DELETE FROM sessions WHERE id = @Id",
            new { Id = sessionId },
            tx);
    }

    public async Task EnsureUserExists(
        IDbConnection conn,
        string userId,
        IDbTransaction tx)
    {
        await conn.ExecuteAsync(
            @"INSERT INTO users (id)
              VALUES (@Id)
              ON CONFLICT (id) DO NOTHING",
            new { Id = userId },
            tx);
    }
    
    public async Task<bool> UserExists(
        IDbConnection conn,
        string userId,
        IDbTransaction tx)
    {
        return await conn.ExecuteScalarAsync<bool>(
            @"SELECT EXISTS (
                SELECT 1 FROM users WHERE id = @Id
            )",
            new { Id = userId },
            tx);
    }

}