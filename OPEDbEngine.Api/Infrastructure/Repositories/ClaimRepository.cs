using Dapper;
using OPEDbEngine.Infrastructure.Sql;
using System.Data;

namespace OPEDbEngine.Infrastructure.Repositories;

public class ClaimRepository
{
    public async Task<Guid?> GetOwner(
        IDbConnection conn,
        Guid nodeId,
        IDbTransaction? tx = null)
    {
        return await conn.ExecuteScalarAsync<Guid?>(
            ClaimSql.GetClaimOwner,
            new { NodeId = nodeId },
            tx);
    }

    public async Task InsertClaim(
        IDbConnection conn,
        Guid nodeId,
        Guid sessionId,
        IDbTransaction? tx = null)
    {
        await conn.ExecuteAsync(
            ClaimSql.InsertClaim,
            new { NodeId = nodeId, Session = sessionId },
            tx);
    }

    public async Task DeleteClaim(
        IDbConnection conn,
        Guid nodeId,
        IDbTransaction? tx = null)
    {
        await conn.ExecuteAsync(
            ClaimSql.DeleteClaim,
            new { NodeId = nodeId },
            tx);
    }
}