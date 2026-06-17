using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Nodes
{
    public class NodeService : INodeService
    {
        private readonly DbConnectionFactory _db;
        private readonly IAttributeSetService _attrService;

        private readonly NodeRepository _nodeRepo;
        private readonly VersionRepository _versionRepo;

        public NodeService(
            DbConnectionFactory db,
            IAttributeSetService attrService,
            NodeRepository nodeRepo,
            VersionRepository versionRepo)
        {
            _db = db;
            _attrService = attrService;
            _nodeRepo = nodeRepo;
            _versionRepo = versionRepo;
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

            // ✅ 1. Check node exists
            if (await _nodeRepo.Exists(conn, nodeId, tx))
                throw new InvalidOperationException("Node already exists.");

            // ✅ 2. Build empty set
            var emptySet = await _attrService.BuildAttributeSetAsync(
                null,
                Enumerable.Empty<AttributeItem>(),
                conn,
                tx);

            // ✅ 3. Create version
            var versionId = Guid.NewGuid();

            // ✅ 4. Insert node
            await _nodeRepo.InsertNode(conn, nodeId, type, owner, versionId, tx);

            // ✅ 5. Insert first version
            await _versionRepo.InsertFirstVersion(
                conn,
                versionId,
                nodeId,
                emptySet,
                sessionId,
                tx);

            tx.Commit();

            return versionId;
        }
    }
}