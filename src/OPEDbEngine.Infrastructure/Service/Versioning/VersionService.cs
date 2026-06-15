using Dapper;
using OPEDbEngine.Infrastructure.Data;

namespace OPEDbEngine.Infrastructure.Service.Versioning
{
    public class VersionService : IVersionService
    {
        private readonly DbConnectionFactory _db;

        public VersionService(DbConnectionFactory db)
        {
            _db = db;
        }

        public async Task<Guid> CreateVersionAsync(
            Guid nodeId,
            Guid expectedVersionId,
            Guid attributeSetId,
            Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            // ✅ Proper node lookup
            var row = await conn.QueryFirstOrDefaultAsync(
                "SELECT current_version_id FROM nodes WHERE id = @NodeId",
                new { NodeId = nodeId },
                tx);

            if (row == null)
                throw new InvalidOperationException("Node does not exist");

            Guid? currentVersion = row.current_version_id;

            // ✅ OCC validation
            if (currentVersion.HasValue)
            {
                if (currentVersion != expectedVersionId)
                    throw new InvalidOperationException("Version mismatch.");
            }
            else
            {
                if (expectedVersionId != Guid.Empty)
                    throw new InvalidOperationException("Invalid initial version.");
            }

            // ✅ Validate attribute set
            var attrExists = await conn.ExecuteScalarAsync<int>(
                "SELECT 1 FROM attribute_sets WHERE id = @Id LIMIT 1",
                new { Id = attributeSetId },
                tx);

            if (attrExists != 1)
                throw new InvalidOperationException("Invalid attribute set.");

            // 2. Create version
            var newVersionId = Guid.NewGuid();

            await conn.ExecuteAsync(
                @"INSERT INTO versions
                (id, node_id, parent_version_id, attribute_set_id, created_by)
                VALUES (@Id, @NodeId, @Parent, @AttrSet, @Session)",
                new
                {
                    Id = newVersionId,
                    NodeId = nodeId,
                    Parent = currentVersion,
                    AttrSet = attributeSetId,
                    Session = sessionId
                },
                tx);

            // 3. Update node pointer
            await conn.ExecuteAsync(
                "UPDATE nodes SET current_version_id = @VersionId WHERE id = @NodeId",
                new { VersionId = newVersionId, NodeId = nodeId },
                tx);

            tx.Commit();
            return newVersionId;
        }
    }
}