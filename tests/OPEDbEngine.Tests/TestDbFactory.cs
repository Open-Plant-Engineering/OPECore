using OPEDbEngine.Infrastructure.Data;
using Dapper;

public static class TestDbFactory
{
    public static DbConnectionFactory Create()
    {
        // ⚠️ Use SAME connection string as your app
        var connStr = "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass";

        return new DbConnectionFactory(connStr);
    }
    public static async Task ResetAsync()
    {
        using var conn = Create().Create();
    
        await conn.ExecuteAsync(@"
            TRUNCATE string_values RESTART IDENTITY CASCADE;
            TRUNCATE number_values CASCADE;
            TRUNCATE bool_values CASCADE;
            TRUNCATE list_values CASCADE;
        ");
    }
}
