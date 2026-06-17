using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using System.Data;
using System.Security.Cryptography;
using OPEDbEngine.Infrastructure.Repositories;

namespace OPEDbEngine.Infrastructure.Services.AttributeSets
{
    public class AttributeSetService : IAttributeSetService
    {
        private readonly AttributeRepository _attributeRepo;

        public AttributeSetService(AttributeRepository attributeRepo)
        {
            _attributeRepo = attributeRepo;
        }

        public async Task<Guid> BuildAttributeSetAsync(
            Guid? existingSetId,
            IEnumerable<AttributeItem> changes,
            IDbConnection conn,
            IDbTransaction tx)
        {
            // ✅ 1. Load existing attributes
            var current = new Dictionary<int, AttributeItem>();

            if (existingSetId.HasValue)
            {
                var rows = await _attributeRepo.GetBySetId(conn, existingSetId.Value, tx);
                
                current = rows.ToDictionary(
                    r => r.Key,
                    r => new AttributeItem
                    {
                        Key = r.Key,
                        ValueHash = r.ValueHash,
                        ValueType = r.ValueType
                    });
            }

            // ✅ 2. Apply changes
            foreach (var change in changes)
            {
                current[change.Key] = change;
            }

            // ✅ 3. Deterministic ordering
            var ordered = current
                .OrderBy(x => x.Key)
                .Select(x => (x.Key, x.Value.ValueHash, x.Value.ValueType));

            var bytes = Serialize(ordered);
            var hash = ComputeHash(bytes);

            // ✅ 4. Check existing set
            var existing = await _attributeRepo.GetSetIdByHash(conn, hash, tx);

            if (existing.HasValue)
                return existing.Value;

            // ✅ 5. Insert new set
            var newSetId = Guid.NewGuid();

            try
            {
                await _attributeRepo.InsertAttributeSet(conn, newSetId, hash, tx);
            }
            catch
            {
                // ✅ concurrent insert safe
                var existingId = await _attributeRepo.GetSetIdByHash(conn, hash, tx);
                return existingId!.Value;

            }

            // ✅ 6. Insert items
            await _attributeRepo.InsertItems(conn, newSetId, current.Values, tx);

            return newSetId;
        }

        // ✅ Helpers

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

        public async Task<Guid> GetOrCreateEmptySetAsync(
            IDbConnection conn,
            IDbTransaction tx)
        {
            // ✅ Try to find existing empty set
            var existing = await _attributeRepo.GetEmptySet(conn, tx);
        
            if (existing != null)
                return existing.Value;
        
            // ✅ Create new empty set
            var newId = Guid.NewGuid();
        
            // ✅ IMPORTANT: hash must NOT be NULL
            var emptyHash = System.Security.Cryptography.SHA256.HashData(Array.Empty<byte>());
        
            await _attributeRepo.InsertAttributeSet(conn, newId, emptyHash, tx);
        
            return newId;
        }
    }
}