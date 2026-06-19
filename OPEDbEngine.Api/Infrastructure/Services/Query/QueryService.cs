using OPEDbEngine.Core.DTOs;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Repositories;
using OPEDbEngine.Infrastructure.Mappers; // ✅ added
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Query
{
    public class QueryService : IQueryService
    {
        private readonly NodeRepository _nodeRepo;
        private readonly VersionRepository _versionRepo;
        private readonly AttributeRepository _attributeRepo;
        private readonly ValueRepository _valueRepo;

        public QueryService(
            NodeRepository nodeRepo,
            VersionRepository versionRepo,
            AttributeRepository attributeRepo,
            ValueRepository valueRepo)
        {
            _nodeRepo = nodeRepo;
            _versionRepo = versionRepo;
            _attributeRepo = attributeRepo;
            _valueRepo = valueRepo;
        }

        public async Task<NodeDto> GetNodeAsync(
            Guid nodeId,
            IDbConnection conn,
            IDbTransaction? tx = null)
        {
            var nodeRow = await _nodeRepo.GetNode(conn, nodeId);

            if (nodeRow == null)
                throw new InvalidOperationException("Node not found");

            var node = NodeMapper.ToDomain(nodeRow); // ✅ mapping

            if (nodeRow.Current_version_id == null)
                throw new InvalidOperationException("Node has no version");

            return await BuildNode(
                conn,
                node.Id,
                node.Type,
                node.Owner,
                nodeRow.Current_version_id.Value,
                tx);
        }

        public async Task<NodeDto> GetNodeVersionAsync(
            Guid nodeId,
            Guid versionId,
            IDbConnection conn,
            IDbTransaction? tx = null)
        {
            var nodeRow = await _nodeRepo.GetNodeMeta(conn, nodeId);

            if (nodeRow == null)
                throw new InvalidOperationException("Node not found");

            var node = NodeMapper.ToDomain(nodeRow); // ✅ mapping

            return await BuildNode(
                conn,
                node.Id,
                node.Type,
                node.Owner,
                versionId,
                tx);
        }

        private async Task<NodeDto> BuildNode(
            IDbConnection conn,
            Guid nodeId,
            string type,
            string owner,
            Guid versionId,
            IDbTransaction? tx)
        {
            var setId = await _versionRepo.GetAttributeSetIdByVersion(conn, versionId);

            var attrs = await _attributeRepo.GetBySetId(conn, setId, tx);

            var result = new NodeDto
            {
                NodeId = nodeId,
                VersionId = versionId,
                Type = type,
                Owner = owner
            };

            foreach (var attr in attrs)
            {
                var value = await ResolveValue(conn, attr.ValueHash, attr.ValueType, tx);

                // ✅ mapping here instead of manual creation
                result.Attributes.Add(AttributeMapper.ToDto(attr, value));
            }

            return result;
        }

        private async Task<object?> ResolveValue(
            IDbConnection conn,
            byte[] hash,
            short type,
            IDbTransaction? tx)
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