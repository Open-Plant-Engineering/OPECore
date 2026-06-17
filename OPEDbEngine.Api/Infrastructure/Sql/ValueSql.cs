namespace OPEDbEngine.Infrastructure.Sql;

public static class ValueSql
{
    public const string InsertString = @"
        INSERT INTO string_values (hash, value)
        VALUES (@Hash, @Value)
        ON CONFLICT (hash) DO NOTHING";

    public const string InsertNumber = @"
        INSERT INTO number_values (hash, value)
        VALUES (@Hash, @Value)
        ON CONFLICT (hash) DO NOTHING";

    public const string InsertBool = @"
        INSERT INTO bool_values (hash, value)
        VALUES (@Hash, @Value)
        ON CONFLICT (hash) DO NOTHING";
}
