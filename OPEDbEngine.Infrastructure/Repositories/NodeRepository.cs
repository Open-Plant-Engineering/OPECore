using Dapper;
using System.Data;

namespace OPEDbEngine.Infrastructure.Repositories
{
    public class NodeRepository
    {
        public async Task<bool> Exists(
            IDbConnection conn,
            Guid nodeId,
            IDbTransaction tx)
        {
            var result = await conn.ExecuteScalarAsync<int>(
                "SELECT 1 FROM nodes WHERE id = @Id LIMIT 1",
                new { Id = nodeId },
                tx);

            return result == 1;
        }
    }
}