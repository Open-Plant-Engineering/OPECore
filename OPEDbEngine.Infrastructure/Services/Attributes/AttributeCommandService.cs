using System.Data;

using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using OPEDbEngine.Infrastructure.Models;

namespace OPEDbEngine.Infrastructure.Services.Attributes
{
    public class AttributeCommandService : IAttributeCommandService
    {
        private readonly DbConnectionFactory _db;
        private readonly IAttributeSetService _attrService;
        private readonly IVersionService _versionService;
        private readonly IClaimService _claim;
        private readonly AttributeRepository _attributeRepo;
        private readonly NodeRepository _nodeRepo;
        private readonly VersionRepository _versionRepo;


        public AttributeCommandService(
            DbConnectionFactory db,
            IAttributeSetService attrService,
            IVersionService versionService,
            IClaimService claimService,
            AttributeRepository attributeRepo,
            NodeRepository nodeRepo,
            VersionRepository versionRepo)
        {
            _db = db;
            _attrService = attrService;
            _versionService = versionService;
            _claim = claimService;
            _attributeRepo = attributeRepo;
            _nodeRepo = nodeRepo;
            _versionRepo = versionRepo;
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
            
            await _claim.ValidateClaimAsync(nodeId, sessionId, conn, tx);
            
            // ✅ 1. Validate node exists
            if (!await _nodeRepo.Exists(conn, nodeId, tx))
                throw new InvalidOperationException("Node does not exist.");

            // ✅ 2. Get current version (NON NULL GUARANTEE)
            var currentVersion = await _versionRepo.GetCurrentVersion(conn, nodeId, tx);

            if (currentVersion == null)
                throw new InvalidOperationException("Node has no version.");

            if (currentVersion.Value != expectedVersionId)
                throw new InvalidOperationException("Version mismatch.");

            // ✅ 3. Get current attribute set (STRICT resolution)
            var currentSet = await _versionRepo.GetAttributeSetId(
                conn,
                currentVersion.Value,
                nodeId,
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

        public async Task<Guid> RemoveAttributeAsync(
            Guid nodeId,
            Guid expectedVersionId,
            int key,
            Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            try
            {
                // ✅ validate claim
                await _claim.ValidateClaimAsync(nodeId, sessionId, conn, tx);

                var currentSet = await _versionRepo.GetAttributeSetId(
                    conn,
                    expectedVersionId,
                    nodeId,
                    tx);

                // ✅ read items
                var rows = await _attributeRepo.GetBySetId(conn, currentSet, tx);

                var items = rows.Select(r => new AttributeItem
                {
                    Key = r.Key,
                    ValueHash = r.ValueHash,
                    ValueType = r.ValueType
                }).ToList();

                // ✅ remove key
                var filtered = items.Where(x => x.Key != key).ToList();
                if (filtered.Count == 0)
                {
                    filtered = new List<AttributeItem>();
                }

                // ✅ build new set
                Guid newSet;
                if (filtered.Count == 0)
                {
                    newSet = await _attrService.GetOrCreateEmptySetAsync(conn, tx);
                }
                else
                {
                    newSet = await _attrService.BuildAttributeSetAsync(
                        currentSet,
                        filtered,
                        conn,
                        tx);
                }

                // ✅ create new version
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
            catch (Exception ex)
            {
                Console.WriteLine(ex.ToString());

                tx.Rollback();
                throw;
            }
        }

        public async Task<Guid> RemoveAttributesAsync(
            Guid nodeId,
            Guid expectedVersionId,
            IEnumerable<int> keys,
            Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();
            using var tx = conn.BeginTransaction();

            await _claim.ValidateClaimAsync(nodeId, sessionId, conn, tx);

            var currentSet = await _versionRepo.GetAttributeSetId(
                conn,
                expectedVersionId,
                nodeId,
                tx);

            var rows = await _attributeRepo.GetBySetId(conn, currentSet, tx);
            
            var items = rows.Select(r => new AttributeItem
            {
                Key = r.Key,
                ValueHash = r.ValueHash,
                ValueType = r.ValueType
            }).ToList();

            var keySet = keys.ToHashSet();

            var filtered = items.Where(x => !keySet.Contains(x.Key)).ToList();

            Guid newSet;
            newSet = await _attrService.BuildAttributeSetAsync(
                currentSet,
                filtered,
                conn,
                tx);

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