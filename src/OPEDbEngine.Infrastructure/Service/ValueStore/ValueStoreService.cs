using Dapper;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Service.Hashing;

namespace OPEDbEngine.Infrastructure.Service.ValueStore;

public class ValueStoreService : IValueStoreService
{
    private readonly DbConnectionFactory _db;
    private readonly IHashService _hash;

    public ValueStoreService(DbConnectionFactory db, IHashService hash)
    {
        _db = db;
        _hash = hash;
    }

    public async Task<byte[]> StoreStringAsync(string value)
    {
        var hash = _hash.HashString(value);

        using var conn = _db.Create();

        var exists = await conn.ExecuteScalarAsync<int>(
            "SELECT 1 FROM string_values WHERE hash = @Hash LIMIT 1",
            new { Hash = hash });

        if (exists == 1)
            return hash;

        await conn.ExecuteAsync(
            "INSERT INTO string_values (hash, value) VALUES (@Hash, @Value)",
            new { Hash = hash, Value = value });

        return hash;
    }

    public async Task<byte[]> StoreNumberAsync(double value)
    {
        var hash = _hash.HashNumber(value);

        using var conn = _db.Create();

        var exists = await conn.ExecuteScalarAsync<int>(
            "SELECT 1 FROM number_values WHERE hash = @Hash LIMIT 1",
            new { Hash = hash });

        if (exists == 1)
            return hash;

        await conn.ExecuteAsync(
            "INSERT INTO number_values (hash, value) VALUES (@Hash, @Value)",
            new { Hash = hash, Value = value });

        return hash;
    }

    public async Task<byte[]> StoreBoolAsync(bool value)
    {
        var hash = _hash.HashBool(value);

        using var conn = _db.Create();

        var exists = await conn.ExecuteScalarAsync<int>(
            "SELECT 1 FROM bool_values WHERE hash = @Hash LIMIT 1",
            new { Hash = hash });

        if (exists == 1)
            return hash;

        await conn.ExecuteAsync(
            "INSERT INTO bool_values (hash, value) VALUES (@Hash, @Value)",
            new { Hash = hash, Value = value });

        return hash;
    }

    public async Task<byte[]> StoreListAsync(byte[] serializedList)
    {
        var hash = _hash.HashBytes(serializedList);

        using var conn = _db.Create();

        var exists = await conn.ExecuteScalarAsync<int>(
            "SELECT 1 FROM list_values WHERE hash = @Hash LIMIT 1",
            new { Hash = hash });

        if (exists == 1)
            return hash;

        await conn.ExecuteAsync(
            "INSERT INTO list_values (hash, value) VALUES (@Hash, @Value)",
            new { Hash = hash, Value = serializedList });

        return hash;
    }
}