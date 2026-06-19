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
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            // ✅ DOMAIN OBJECT INTRODUCED
            var node = new Node
            {
                Id = nodeId,
                Type = type,
                Owner = owner
            };

            // ✅ 1. Check node exists
            if (await _nodeRepo.Exists(conn, node.Id, tx))
                throw new InvalidOperationException("Node already exists.");

            // ✅ 2. Build empty set (domain already used)
            var emptySet = await _attrService.BuildAttributeSetAsync(
                null,
                Enumerable.Empty<AttributeItem>(),
                conn,
                tx);

            // ✅ 3. Create version
            var versionId = Guid.NewGuid();

            // ✅ 4. Insert node using domain data
            await _nodeRepo.InsertNode(
                conn,
                node.Id,
                node.Type,
                node.Owner,
                versionId,
                tx);

            // ✅ 5. Insert first version
            await _versionRepo.InsertFirstVersion(
                conn,
                versionId,
                node.Id,
                emptySet,
                sessionId,
                tx);

            return versionId;
        }
    }
}
