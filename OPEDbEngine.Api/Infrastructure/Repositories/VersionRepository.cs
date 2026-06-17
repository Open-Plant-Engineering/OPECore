using Dapper;
using System.Data;

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
                "SELECT current_version_id FROM nodes WHERE id = @Id",
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
                @"SELECT attribute_set_id
                  FROM versions
                  WHERE id = @VersionId AND node_id = @NodeId",
                new { VersionId = versionId, NodeId = nodeId },
                tx);
        }
    }
}