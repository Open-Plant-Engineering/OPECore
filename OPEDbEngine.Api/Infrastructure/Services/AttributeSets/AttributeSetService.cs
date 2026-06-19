using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using System.Data;
using System.Security.Cryptography;
using OPEDbEngine.Infrastructure.Repositories;
using OPEDbEngine.Infrastructure.Mappers;

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
            var current = new Dictionary<int, AttributeItem>();

            if (existingSetId.HasValue)
            {
                var rows = await _attributeRepo.GetBySetId(conn, existingSetId.Value, tx);

                current = rows.ToDictionary(
                    r => r.Key,
                    r => AttributeMapper.ToDomain(r) // ✅ CHANGED
                );
            }

            foreach (var change in changes)
            {
                current[change.Key] = change;
            }

            var ordered = current
                .OrderBy(x => x.Key)
                .Select(x => (x.Key, x.Value.ValueHash, x.Value.ValueType));

            var bytes = Serialize(ordered);
            var hash = ComputeHash(bytes);

            var existing = await _attributeRepo.GetSetIdByHash(conn, hash, tx);

            if (existing.HasValue)
                return existing.Value;

            var newSetId = Guid.NewGuid();

            try
            {
                await _attributeRepo.InsertAttributeSet(conn, newSetId, hash, tx);
            }
            catch
            {
                var existingId = await _attributeRepo.GetSetIdByHash(conn, hash, tx);
                return existingId!.Value;
            }

            await _attributeRepo.InsertItems(conn, newSetId, current.Values, tx);

            return newSetId;
        }

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
            var existing = await _attributeRepo.GetEmptySet(conn, tx);

            if (existing != null)
                return existing.Value;

            var newId = Guid.NewGuid();

            var emptyHash = System.Security.Cryptography.SHA256.HashData(Array.Empty<byte>());

            await _attributeRepo.InsertAttributeSet(conn, newId, emptyHash, tx);

            return newId;
        }
    }
}