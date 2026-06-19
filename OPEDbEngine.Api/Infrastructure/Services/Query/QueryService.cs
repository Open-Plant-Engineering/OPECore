using OPEDbEngine.Core.DTOs;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Mappers;
using OPEDbEngine.Infrastructure.Repositories;
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

            // ✅ ROW → DOMAIN
            var node = NodeMapper.ToDomain(nodeRow);

            if (nodeRow.Current_version_id == null)
                throw new InvalidOperationException("Node has no version");

            return await BuildNode(
                node,
                nodeRow.Current_version_id.Value,
                conn,
                tx);
        }

        public async Task<NodeDto> GetNodeVersionAsync(
            Guid nodeId,
            Guid versionId,
            IDbConnection conn,
            IDbTransaction? tx = null)
        {
            var nodeMetaRow = await _nodeRepo.GetNodeMeta(conn, nodeId);

            if (nodeMetaRow == null)
                throw new InvalidOperationException("Node not found");

            // ✅ ROW → DOMAIN
            var node = NodeMapper.ToDomain(nodeMetaRow);

            return await BuildNode(
                node,
                versionId,
                conn,
                tx);
        }

        // ✅ DOMAIN-DRIVEN method
        private async Task<NodeDto> BuildNode(
            Node node,
            Guid versionId,
            IDbConnection conn,
            IDbTransaction? tx)
        {
            // ✅ VERSION resolution still from DB (can later map if needed)
            var setId = await _versionRepo.GetAttributeSetIdByVersion(conn, versionId);

            var attrRows = await _attributeRepo.GetBySetId(conn, setId, tx);

            var result = new NodeDto
            {
                NodeId = node.Id,
                VersionId = versionId,
                Type = node.Type,
                Owner = node.Owner
            };

            foreach (var row in attrRows)
            {
                var value = await ResolveValue(conn, row.ValueHash, row.ValueType, tx);

                // ✅ ROW → DTO via mapper
                result.Attributes.Add(AttributeMapper.ToDto(row, value));
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
