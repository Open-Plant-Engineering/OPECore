using Dapper;
using System.Data;
using OPEDbEngine.Infrastructure.Sql;

namespace OPEDbEngine.Infrastructure.Repositories
{
    public class VersionRepository
    {
        public async Task<Guid?> GetCurrentVersion(
            IDbConnection conn,
            Guid nodeId,
            IDbTransaction tx)
        {
            return await conn.ExecuteScalarAsync<Guid?>(
                VersionSql.GetCurrentVersion,
                new { Id = nodeId },
                tx);
        }

        public async Task<Guid> GetAttributeSetId(
            IDbConnection conn,
            Guid versionId,
            Guid nodeId,
            IDbTransaction tx)
        {
            return await conn.ExecuteScalarAsync<Guid>(
                VersionSql.GetAttributeSetId,
                new { VersionId = versionId, NodeId = nodeId },
                tx);
        }

        public async Task InsertFirstVersion(
            IDbConnection conn,
            Guid versionId,
            Guid nodeId,
            Guid attrSet,
            Guid sessionId,
            IDbTransaction tx)
        {
            await conn.ExecuteAsync(
                VersionSql.InsertFirstVersion,
                new
                {
                    Id = versionId,
                    NodeId = nodeId,
                    AttrSet = attrSet,
                    Session = sessionId
                },
                tx);
        }

        public async Task<Guid> GetAttributeSetIdByVersion(
            IDbConnection conn,
            Guid versionId)
        {
            return await conn.ExecuteScalarAsync<Guid>(
                QuerySql.GetAttributeSet,
                new { Id = versionId });
        }
    }
}