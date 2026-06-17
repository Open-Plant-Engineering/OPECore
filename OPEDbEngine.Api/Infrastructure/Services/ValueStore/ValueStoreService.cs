using Dapper;
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

        public async Task<byte[]> StoreStringAsync(string value)
        {
            var hash = _hash.HashString(value);

            using var conn = _db.Create();

            await _valueRepo.InsertString(conn, hash, value);

            return hash;
        }

        public async Task<byte[]> StoreNumberAsync(double value)
        {
            var hash = _hash.HashNumber(value);

            using var conn = _db.Create();

            await _valueRepo.InsertNumber(conn, hash, value);

            return hash;
        }

        public async Task<byte[]> StoreBoolAsync(bool value)
        {
            var hash = _hash.HashBool(value);

            using var conn = _db.Create();

            await _valueRepo.InsertBool(conn, hash, value);

            return hash;
        }
    }
}