using Dapper;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using OPEDbEngine.Infrastructure.Service.Versioning;

namespace OPEDbEngine.Infrastructure.Service.Attributes
{
    public class AttributeCommandService : IAttributeCommandService
    {
        private readonly DbConnectionFactory _db;
        private readonly IAttributeSetService _attrService;
        private readonly IVersionService _versionService;

        public AttributeCommandService(
            DbConnectionFactory db,
            IAttributeSetService attrService,
            IVersionService versionService)
        {
            _db = db;
            _attrService = attrService;
            _versionService = versionService;
        }

        public async Task<Guid> SetAttributeAsync(
            Guid nodeId,
            Guid expectedVersionId,
            int key,
            byte[] valueHash,
            short valueType,
            Guid sessionId)
        {
            var item = new AttributeItem
            {
                Key = key,
                ValueHash = valueHash,
                ValueType = valueType
            };

            return await BulkSetAttributesAsync(
                nodeId,
                expectedVersionId,
                new[] { item },
                sessionId);
        }

        public async Task<Guid> BulkSetAttributesAsync(
            Guid nodeId,
            Guid expectedVersionId,
            IEnumerable<AttributeItem> items,
            Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            // ✅ 1. Claim validation
            var claimedBy = await conn.ExecuteScalarAsync<Guid?>(
                "SELECT claimed_by FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId });

            if (!claimedBy.HasValue)
                throw new InvalidOperationException("Node must be claimed before modification.");

            if (claimedBy.Value != sessionId)
                throw new InvalidOperationException("Node claimed by another session.");

            // ✅ 2. Get current version
            var row = await conn.QueryFirstOrDefaultAsync(
                "SELECT current_version_id FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            if (row == null)
                throw new InvalidOperationException("Node does not exist.");

            Guid? currentVersion = row.current_version_id;

            if (currentVersion != expectedVersionId)
                throw new InvalidOperationException("Version mismatch.");

            // ✅ 3. Get current attribute set
            var currentSet = await conn.ExecuteScalarAsync<Guid>(
                "SELECT attribute_set_id FROM versions WHERE id = @VersionId",
                new { VersionId = currentVersion });

            // ✅ 4. Build new attribute set
            var newSet = await _attrService.BuildAttributeSetAsync(
                currentSet,
                items);

            // ✅ 5. Create new version
            var newVersion = await _versionService.CreateVersionAsync(
                nodeId,
                expectedVersionId,
                newSet,
                sessionId);

            return newVersion;
        }
    }
}