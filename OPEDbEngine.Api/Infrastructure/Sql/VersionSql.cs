namespace OPEDbEngine.Infrastructure.Sql;

public static class VersionSql
{
    public const string InsertFirstVersion = @"
        INSERT INTO versions
        (id, node_id, parent_version_id, attribute_set_id, created_by)
        VALUES (@Id, @NodeId, NULL, @AttrSet, @Session)";

    public const string GetCurrentVersion = @"
        SELECT current_version_id
        FROM nodes
        WHERE id = @Id";

    public const string GetAttributeSetId = @"
        SELECT attribute_set_id
        FROM versions
        WHERE id = @VersionId AND node_id = @NodeId";

    public const string InsertVersion = @"
        INSERT INTO versions
        (id, node_id, parent_version_id, attribute_set_id, created_by)
        VALUES (@Id, @NodeId, @Parent, @AttrSet, @Session)";

    public const string UpdateNodeVersion = @"
        UPDATE nodes
        SET current_version_id = @Version
        WHERE id = @NodeId
        AND current_version_id = @Expected";
}
