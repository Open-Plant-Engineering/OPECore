using Dapper;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using System.Security.Cryptography;

namespace OPEDbEngine.Infrastructure.Service.AttributeSets
{
    public class AttributeSetService : IAttributeSetService
    {
        private readonly DbConnectionFactory _db;

        public AttributeSetService(DbConnectionFactory db)
        {
            _db = db;
        }

        public async Task<Guid> BuildAttributeSetAsync(
            Guid? existingSetId,
            IEnumerable<AttributeItem> changes)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            // 1. Load existing attributes
            var current = new Dictionary<int, AttributeItem>();

            if (existingSetId.HasValue)
            {
                var rows = await conn.QueryAsync<AttributeItem>(
                    @"SELECT key as Key, value_hash as ValueHash, value_type as ValueType
                      FROM attribute_set_items
                      WHERE set_id = @SetId",
                    new { SetId = existingSetId },
                    tx);

                current = rows.ToDictionary(x => x.Key, x => x);
            }

            // 2. Apply changes
            foreach (var change in changes)
            {
                current[change.Key] = change;
            }

            // 3. Sort + serialize for hashing
            var ordered = current
                .OrderBy(x => x.Key)
                .Select(x => (x.Key, x.Value.ValueHash, x.Value.ValueType));

            var bytes = Serialize(ordered);

            var hash = ComputeHash(bytes);

            // 4. Check existing set
            var existing = await conn.ExecuteScalarAsync<Guid?>(
                "SELECT id FROM attribute_sets WHERE hash = @Hash",
                new { Hash = hash },
                tx);

            if (existing.HasValue)
            {
                tx.Commit();
                return existing.Value;
            }

            // 5. Create new set
            var newSetId = Guid.NewGuid();

            try
            {
                await conn.ExecuteAsync(
                    "INSERT INTO attribute_sets (id, hash) VALUES (@Id, @Hash)",
                    new { Id = newSetId, Hash = hash },
                    tx);
            }
            catch
            {
                // race condition fallback
                var existingId = await conn.ExecuteScalarAsync<Guid>(
                    "SELECT id FROM attribute_sets WHERE hash = @Hash",
                    new { Hash = hash },
                    tx);

                tx.Commit();
                return existingId;
            }

            // 6. Insert items
            foreach (var item in current.Values)
            {
                await conn.ExecuteAsync(
                    @"INSERT INTO attribute_set_items
                      (set_id, key, value_hash, value_type)
                      VALUES (@SetId, @Key, @ValueHash, @ValueType)",
                    new
                    {
                        SetId = newSetId,
                        Key = item.Key,
                        ValueHash = item.ValueHash,
                        ValueType = item.ValueType
                    },
                    tx);
            }

            tx.Commit();
            return newSetId;
        }

        // Helpers

        private byte[] ComputeHash(byte[] input)
        {
            using var sha = SHA256.Create();
            return sha.ComputeHash(input);
        }

        private byte[] Serialize(IEnumerable<(int Key, byte[] Hash, short Type)> items)
        {
            using var ms = new MemoryStream();
            using var writer = new BinaryWriter(ms);

            foreach (var item in items)
            {
                writer.Write(item.Key);
                writer.Write(item.Type);
                writer.Write(item.Hash.Length);
                writer.Write(item.Hash);
            }

            return ms.ToArray();
        }
    }
}