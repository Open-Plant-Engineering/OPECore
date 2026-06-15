using Dapper;
using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;
using StackExchange.Redis;
using System.Text.Json;
using OPEDbEngine.Infrastructure.Data;

namespace OPEDbEngine.Infrastructure.Repositories;

public class UserRepository : IUserRepository
{
    private readonly DbConnectionFactory _db;
    private readonly IDatabase _redis;

    public UserRepository(DbConnectionFactory db, IConnectionMultiplexer redis)
    {
        _db = db;
        _redis = redis.GetDatabase();
    }

    public async Task<User?> GetByIdAsync(Guid id)
    {
        var cacheKey = $"user:{id}";

        // Redis check
        var cached = await _redis.StringGetAsync(cacheKey);
        if (!cached.IsNullOrEmpty)
        {
            return JsonSerializer.Deserialize<User>(cached!);
        }

        using var connection = _db.Create();

        var user = await connection.QueryFirstOrDefaultAsync<User>(
            "SELECT id, name, email FROM users WHERE id = @Id",
            new { Id = id });

        if (user != null)
        {
            await _redis.StringSetAsync(cacheKey,
                JsonSerializer.Serialize(user),
                TimeSpan.FromMinutes(5));
        }

        return user;
    }


    public async Task<Guid> CreateAsync(User user)
    {
        using var connection = _db.Create();

        await connection.ExecuteAsync(
            "INSERT INTO users (id, name, email) VALUES (@Id, @Name, @Email)",
            user);

        var cacheKey = $"user:{user.Id}";
        await _redis.KeyDeleteAsync(cacheKey);

        return user.Id;
    }

}
