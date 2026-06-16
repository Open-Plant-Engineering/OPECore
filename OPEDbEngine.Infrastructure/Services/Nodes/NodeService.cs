using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Nodes
{
    public class NodeService : INodeService
    {
        private readonly DbConnectionFactory _db;
        private readonly IAttributeSetService _attrService;

        public NodeService(
            DbConnectionFactory db,
            IAttributeSetService attrService)
        {
            _db = db;
            _attrService = attrService;
        }
        
        public async Task<Guid> CreateNodeAsync(
            Guid nodeId,
            string type,
            string owner,
            Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            // ✅ 1. Ensure node does not exist
            var exists = await conn.ExecuteScalarAsync<int>(
                "SELECT 1 FROM nodes WHERE id = @Id LIMIT 1",
                new { Id = nodeId },
                tx);

            if (exists == 1)
                throw new InvalidOperationException("Node already exists.");

            // ✅ 2. Create EMPTY attribute set FIRST
            var emptySet = await _attrService.BuildAttributeSetAsync(
                null,
                Enumerable.Empty<AttributeItem>(),
                conn,
                tx);

            // ✅ 3. Generate versionId ONCE
            var versionId = Guid.NewGuid();

            // ✅ 4. Insert node WITH version (never null)
            await conn.ExecuteAsync(
                @"INSERT INTO nodes (id, type, owner, current_version_id)
                  VALUES (@Id, @Type, @Owner, @Version)",
                new
                {
                    Id = nodeId,
                    Type = type,
                    Owner = owner,
                    Version = versionId
                },
                tx);

            // ✅ 5. Insert FIRST version ONLY ONCE
            await conn.ExecuteAsync(
                @"INSERT INTO versions
                  (id, node_id, parent_version_id, attribute_set_id, created_by)
                  VALUES (@Id, @NodeId, NULL, @AttrSet, @Session)",
                new
                {
                    Id = versionId,
                    NodeId = nodeId,
                    AttrSet = emptySet,
                    Session = sessionId
                },
                tx);

            tx.Commit();

            return versionId;
        }
    }
}