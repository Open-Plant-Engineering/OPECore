using OPEDbEngine.Core.DTOs;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Query
{
    public class QueryService : IQueryService
    {
        private readonly DbConnectionFactory _db;
        private readonly NodeRepository _nodeRepo;
        private readonly VersionRepository _versionRepo;
        private readonly AttributeRepository _attributeRepo;
        private readonly ValueRepository _valueRepo;

        public QueryService(
            DbConnectionFactory db,
            NodeRepository nodeRepo,
            VersionRepository versionRepo,
            AttributeRepository attributeRepo,
            ValueRepository valueRepo)
        {
            _db = db;
            _nodeRepo = nodeRepo;
            _versionRepo = versionRepo;
            _attributeRepo = attributeRepo;
            _valueRepo = valueRepo;
        }

        public async Task<NodeDto> GetNodeAsync(Guid nodeId)
        {
            using var conn = _db.Create();

            var node = await _nodeRepo.GetNode(conn, nodeId);

            if (node == null)
                throw new InvalidOperationException("Node not found");

            // ✅ Defensive re-check (important for consistency)
            if (node.current_version_id == null)
            {
                node = await _nodeRepo.GetNode(conn, nodeId);

                if (node!.current_version_id == null)
                    throw new InvalidOperationException("Node has no version");
            }

            return await BuildNode(
                conn,
                nodeId,
                node.Type,
                node.Owner,
                node.current_version_id.Value);
        }

        public async Task<NodeDto> GetNodeVersionAsync(Guid nodeId, Guid versionId)
        {
            using var conn = _db.Create();

            var node = await _nodeRepo.GetNodeMeta(conn, nodeId);

            if (node == null)
                throw new InvalidOperationException("Node not found");

            return await BuildNode(conn, nodeId, node.Type, node.Owner, versionId);
        }

        private async Task<NodeDto> BuildNode(
            IDbConnection conn,
            Guid nodeId,
            string type,
            string owner,
            Guid versionId)
        {
            // ✅ get attribute set
            var setId = await _versionRepo.GetAttributeSetIdByVersion(conn, versionId);

            // ✅ get attributes
            var attrs = await _attributeRepo.GetBySetId(conn, setId);

            var result = new NodeDto
            {
                NodeId = nodeId,
                VersionId = versionId,
                Type = type,
                Owner = owner
            };

            // ✅ resolve values
            foreach (var attr in attrs)
            {
                var value = await ResolveValue(conn, attr.ValueHash, attr.ValueType);

                result.Attributes.Add(new AttributeDto
                {
                    Key = attr.Key,
                    ValueType = attr.ValueType,
                    Value = value
                });
            }

            return result;
        }

        private async Task<object?> ResolveValue(
            IDbConnection conn,
            byte[] hash,
            short type)
        {
            return type switch
            {
                1 => await _valueRepo.GetString(conn, hash),
                2 => await _valueRepo.GetNumber(conn, hash),
                3 => await _valueRepo.GetBool(conn, hash),
                _ => throw new InvalidOperationException("Unsupported type")
            };
        }
    }
}