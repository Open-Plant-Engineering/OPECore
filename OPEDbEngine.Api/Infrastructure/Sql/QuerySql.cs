namespace OPEDbEngine.Infrastructure.Sql;

public static class QuerySql
{
    public const string GetNode = @"
        SELECT id, type, owner, current_version_id
        FROM nodes
        WHERE id = @Id";

    public const string GetNodeMeta = @"
        SELECT id, type, owner
        FROM nodes
        WHERE id = @Id";

    public const string GetAttributeSet = @"
        SELECT attribute_set_id
        FROM versions
        WHERE id = @Id";

    public const string GetStringValue = @"
        SELECT value FROM string_values WHERE hash = @Hash";

    public const string GetNumberValue = @"
        SELECT value FROM number_values WHERE hash = @Hash";

    public const string GetBoolValue = @"
        SELECT value FROM bool_values WHERE hash = @Hash";
}