using Dapper;
using OPEDbEngine.Infrastructure.Data;

public static class TestDbFactory
{
    public static DbConnectionFactory Create()
    {
        var connStr =
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass";

        return new DbConnectionFactory(connStr);
    }

    public static async Task ResetAsync()
    {
        using var conn = Create().Create();
        conn.Open();

        // ✅ IMPORTANT: correct order (child → parent)
        await conn.ExecuteAsync(@"
            TRUNCATE node_claims CASCADE;
            TRUNCATE nodes CASCADE;
            TRUNCATE versions CASCADE;
            TRUNCATE attribute_set_items CASCADE;
            TRUNCATE attribute_sets CASCADE;

            TRUNCATE string_values CASCADE;
            TRUNCATE number_values CASCADE;
            TRUNCATE bool_values CASCADE;
        ");
    }
}