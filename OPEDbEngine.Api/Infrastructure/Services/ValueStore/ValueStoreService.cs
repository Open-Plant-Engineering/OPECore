using System.Data;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using OPEDbEngine.Infrastructure.Services.Hashing;

namespace OPEDbEngine.Infrastructure.Services.ValueStore
{
    public interface IValueStoreService
    {
        Task<byte[]> StoreStringAsync(string value);
        Task<byte[]> StoreNumberAsync(double value);
        Task<byte[]> StoreBoolAsync(bool value);
    }
    public class ValueStoreService : IValueStoreService
    {
        private readonly DbConnectionFactory _db;
        private readonly IHashService _hash;
        private readonly ValueRepository _valueRepo;

        public ValueStoreService(
            DbConnectionFactory db,
            IHashService hash,
            ValueRepository valueRepo)
        {
            _db = db;
            _hash = hash;
            _valueRepo = valueRepo;
        }

        // ✅ TRANSACTIONAL VERSION (NEW PRIMARY)
        public async Task<byte[]> StoreStringAsync(
            string value,
            IDbConnection conn,
            IDbTransaction? tx = null)
        {
            var hash = _hash.HashString(value);
            await _valueRepo.InsertString(conn, hash, value);
            return hash;
        }

        // ✅ SIMPLE VERSION (WRAPPER)
        public async Task<byte[]> StoreStringAsync(string value)
        {
            using var conn = _db.Create();
            conn.Open();
            return await StoreStringAsync(value, conn, null);
        }

        public async Task<byte[]> StoreNumberAsync(
            double value,
            IDbConnection conn,
            IDbTransaction? tx = null)
        {
            var hash = _hash.HashNumber(value);
            await _valueRepo.InsertNumber(conn, hash, value);
            return hash;
        }

        public async Task<byte[]> StoreNumberAsync(double value)
        {
            using var conn = _db.Create();
            conn.Open();
            return await StoreNumberAsync(value, conn, null);
        }

        public async Task<byte[]> StoreBoolAsync(
            bool value,
            IDbConnection conn,
            IDbTransaction? tx = null)
        {
            var hash = _hash.HashBool(value);
            await _valueRepo.InsertBool(conn, hash, value);
            return hash;
        }

        public async Task<byte[]> StoreBoolAsync(bool value)
        {
            using var conn = _db.Create();
            conn.Open();
            return await StoreBoolAsync(value, conn, null);
        }
    }
}