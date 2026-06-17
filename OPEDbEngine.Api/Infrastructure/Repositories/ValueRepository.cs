using Dapper;
using System.Data;
using OPEDbEngine.Infrastructure.Sql;

namespace OPEDbEngine.Infrastructure.Repositories;

public class ValueRepository
{
    public async Task<string?> GetString(IDbConnection conn, byte[] hash)
    {
        return await conn.ExecuteScalarAsync<string?>(
            QuerySql.GetStringValue,
            new { Hash = hash });
    }

    public async Task<double?> GetNumber(IDbConnection conn, byte[] hash)
    {
        return await conn.ExecuteScalarAsync<double?>(
            QuerySql.GetNumberValue,
            new { Hash = hash });
    }

    public async Task<bool?> GetBool(IDbConnection conn, byte[] hash)
    {
        return await conn.ExecuteScalarAsync<bool?>(
            QuerySql.GetBoolValue,
            new { Hash = hash });
    }

    public async Task InsertString(
        IDbConnection conn,
        byte[] hash,
        string value)
    {
        await conn.ExecuteAsync(
            ValueSql.InsertString,
            new { Hash = hash, Value = value });
    }

    public async Task InsertNumber(
        IDbConnection conn,
        byte[] hash,
        double value)
    {
        await conn.ExecuteAsync(
            ValueSql.InsertNumber,
            new { Hash = hash, Value = value });
    }

    public async Task InsertBool(
        IDbConnection conn,
        byte[] hash,
        bool value)
    {
        await conn.ExecuteAsync(
            ValueSql.InsertBool,
            new { Hash = hash, Value = value });
    }

}