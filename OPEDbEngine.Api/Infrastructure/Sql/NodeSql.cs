namespace OPEDbEngine.Infrastructure.Sql;

public static class NodeSql
{
    public const string Exists = @"
        SELECT 1
        FROM nodes
        WHERE id = @Id
        LIMIT 1";

    public const string InsertNode = @"
        INSERT INTO nodes (id, type, owner, current_version_id)
        VALUES (@Id, @Type, @Owner, @Version)";
}
