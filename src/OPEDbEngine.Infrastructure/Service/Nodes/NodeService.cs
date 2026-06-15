using Dapper;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using OPEDbEngine.Infrastructure.Service.Versioning;

namespace OPEDbEngine.Infrastructure.Service.Nodes
{
    public class NodeService : INodeService
    {
        private readonly DbConnectionFactory _db;
        private readonly IAttributeSetService _attrService;
        private readonly IVersionService _versionService;

        public NodeService(
            DbConnectionFactory db,
            IAttributeSetService attrService,
            IVersionService versionService)
        {
            _db = db;
            _attrService = attrService;
            _versionService = versionService;
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

            // ✅ 1. Check if node already exists
            var exists = await conn.ExecuteScalarAsync<int>(
                "SELECT 1 FROM nodes WHERE id = @Id LIMIT 1",
                new { Id = nodeId },
                tx);

            if (exists == 1)
                throw new InvalidOperationException("Node already exists.");

            // ✅ 2. Insert node (no version yet)
            await conn.ExecuteAsync(
                @"INSERT INTO nodes (id, type, owner) 
                  VALUES (@Id, @Type, @Owner)",
                new
                {
                    Id = nodeId,
                    Type = type,
                    Owner = owner
                },
                tx);

            tx.Commit(); // ✅ commit early before calling services

            // ✅ 3. Create EMPTY attribute set
            var emptySet = await _attrService.BuildAttributeSetAsync(
                null,
                Enumerable.Empty<AttributeItem>());

            // ✅ 4. Create FIRST version
            var v1 = await _versionService.CreateVersionAsync(
                nodeId,
                Guid.Empty,
                emptySet,
                sessionId);

            return v1;
        }
    }
}