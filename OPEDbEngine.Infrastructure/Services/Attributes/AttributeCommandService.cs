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
        private readonly IClaimService _claim;

        public AttributeCommandService(
            DbConnectionFactory db,
            IAttributeSetService attrService,
            IVersionService versionService,
            IClaimService claimService)
        {
            _db = db;
            _attrService = attrService;
            _versionService = versionService;
            _claim = claimService;
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

    public async Task<Guid> RemoveAttributeAsync(
        Guid nodeId,
        Guid expectedVersionId,
        int key,
        Guid sessionId)
    {
        using var conn = _db.Create();
        conn.Open();
    
        using var tx = conn.BeginTransaction();
    
        // ✅ Print versions table columns
        var columns = await conn.QueryAsync<string>(
            @"SELECT column_name
              FROM information_schema.columns
              WHERE table_name = 'versions'
              ORDER BY ordinal_position");
    
        try
        {
            // ✅ validate claim
            await _claim.ValidateClaimAsync(nodeId, sessionId, conn, tx);
    
            var currentSet = await conn.ExecuteScalarAsync<Guid>(
                @"SELECT attribute_set_id
                  FROM versions
                  WHERE id = @VersionId AND node_id = @NodeId",
                new { VersionId = expectedVersionId, NodeId = nodeId },
                tx);
    
            // ✅ read items
            var items = (await conn.QueryAsync<AttributeItem>(
                @"SELECT key, value_hash as ValueHash, value_type as ValueType
                  FROM attribute_set_items
                  WHERE set_id = @SetId",
                new { SetId = currentSet },
                tx)).ToList();
    
            // ✅ remove key
            var filtered = items.Where(x => x.Key != key).ToList();
            if (filtered.Count == 0)
            {
                Console.WriteLine("⚠️ All attributes removed → creating empty set");
                filtered = new List<AttributeItem>();
            }
    
            // ✅ build new set
            Guid newSet;

            if (filtered.Count == 0)
            {
                // ✅ Try to find existing empty set first
                newSet = await conn.ExecuteScalarAsync<Guid?>(
                    @"SELECT id FROM attribute_sets WHERE id NOT IN
                      (SELECT DISTINCT set_id FROM attribute_set_items)
                      LIMIT 1",
                    transaction: tx) ?? Guid.NewGuid();

                // ✅ If not found, create new empty set
                if (newSet == Guid.Empty)
                {
                    newSet = Guid.NewGuid();

                    await conn.ExecuteAsync(
                        "INSERT INTO attribute_sets (id) VALUES (@Id)",
                        new { Id = newSet },
                        tx);
                }
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
            Console.WriteLine("❌ RemoveAttribute FAILED");
            Console.WriteLine(ex.ToString());
    
            tx.Rollback();
            throw;
        }
    }
    
    }
}