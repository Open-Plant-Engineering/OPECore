using Dapper;
using OPEDbEngine.Core.Interfaces;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Versioning
{
    public class VersionService : IVersionService
    {
        public async Task<Guid> CreateVersionAsync(
            Guid nodeId,
            Guid expectedVersionId,
            Guid attributeSetId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            // ✅ DO NOT re-read version
            // ✅ TRUST expectedVersionId

            var newVersionId = Guid.NewGuid();

            // ✅ Insert new version
            await conn.ExecuteAsync(
                @"INSERT INTO versions
                  (id, node_id, parent_version_id, attribute_set_id, created_by)
                  VALUES (@Id, @NodeId, @Parent, @AttrSet, @Session)",
                new
                {
                    Id = newVersionId,
                    NodeId = nodeId,
                    Parent = expectedVersionId,   // ✅ TRUST caller
                    AttrSet = attributeSetId,
                    Session = sessionId
                },
                tx);

            // ✅ Update node pointer
            var rows = await conn.ExecuteAsync(
                @"UPDATE nodes
                  SET current_version_id = @Version
                  WHERE id = @NodeId
                  AND current_version_id = @Expected",   // ✅ OCC check here
                new
                {
                    Version = newVersionId,
                    NodeId = nodeId,
                    Expected = expectedVersionId
                },
                tx);

            // ✅ Ensure exactly one row updated
            if (rows != 1)
                throw new InvalidOperationException("Version mismatch.");

            return newVersionId;
        }
    }
}