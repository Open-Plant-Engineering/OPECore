using Dapper;
using OPEDbEngine.Infrastructure.Sql;
using System.Data;
using OPEDbEngine.Infrastructure.Models;

namespace OPEDbEngine.Infrastructure.Repositories;

public class NodeRepository
{
    public async Task<bool> Exists(
        IDbConnection conn,
        Guid nodeId,
        IDbTransaction tx)
    {
        var result = await conn.ExecuteScalarAsync<int?>(
            NodeSql.Exists,
            new { Id = nodeId },
            tx);

        return result == 1;
    }

    public async Task InsertNode(
        IDbConnection conn,
        Guid nodeId,
        string type,
        string owner,
        Guid versionId,
        IDbTransaction tx)
    {
        await conn.ExecuteAsync(
            NodeSql.InsertNode,
            new
            {
                Id = nodeId,
                Type = type,
                Owner = owner,
                Version = versionId
            },
            tx);
    }

    public async Task<NodeRow?> GetNode(
        IDbConnection conn,
        Guid nodeId)
    {
        return await conn.QueryFirstOrDefaultAsync<NodeRow>(
            QuerySql.GetNode,
            new { Id = nodeId });
    }

    public async Task<NodeMeta?> GetNodeMeta(
        IDbConnection conn,
        Guid nodeId)
    {
        return await conn.QueryFirstOrDefaultAsync<NodeMeta>(
            QuerySql.GetNodeMeta,
            new { Id = nodeId });
    }
}