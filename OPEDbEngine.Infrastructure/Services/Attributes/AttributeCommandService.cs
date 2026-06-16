using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Attributes
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

            using var tx = conn.BeginTransaction();

            // ✅ 1. Validate node exists
            var exists = await conn.ExecuteScalarAsync<int>(
                "SELECT 1 FROM nodes WHERE id = @Id LIMIT 1",
                new { Id = nodeId },
                tx);

            if (exists != 1)
                throw new InvalidOperationException("Node does not exist.");

            // ✅ 2. Get current version (NON NULL GUARANTEE)
            var currentVersion = await conn.ExecuteScalarAsync<Guid?>(
                "SELECT current_version_id FROM nodes WHERE id = @Id",
                new { Id = nodeId },
                tx);

            if (currentVersion == null)
                throw new InvalidOperationException("Node has no version.");

            if (currentVersion.Value != expectedVersionId)
                throw new InvalidOperationException("Version mismatch.");

            // ✅ 3. Get current attribute set (STRICT resolution)
            var currentSet = await conn.ExecuteScalarAsync<Guid>(
                @"SELECT attribute_set_id 
                  FROM versions 
                  WHERE id = @Id",
                new { Id = currentVersion.Value },   // ✅ FORCE NON-NULL
                tx);

            // ✅ 4. Build new attribute set
            var newSet = await _attrService.BuildAttributeSetAsync(
                currentSet,
                items,
                conn,
                tx);

            // ✅ 5. Create new version (same TX)
            var newVersion = await _versionService.CreateVersionAsync(
                nodeId,
                expectedVersionId,
                newSet,
                sessionId,
                conn,
                tx);

            tx.Commit();

            return newVersion;
        }
    }
}