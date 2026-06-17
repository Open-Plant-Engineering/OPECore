namespace OPEDbEngine.Infrastructure.Sql;

public static class AttributeSql
{
    public const string GetItemsBySetId = @"
        SELECT set_id     AS SetId,
               key,
               value_hash AS ValueHash,
               value_type AS ValueType
        FROM attribute_set_items
        WHERE set_id = @SetId";

    public const string GetSetByHash = @"
        SELECT id FROM attribute_sets WHERE hash = @Hash";

    public const string InsertAttributeSet = @"
        INSERT INTO attribute_sets (id, hash)
        VALUES (@Id, @Hash)";

    public const string InsertAttributeItem = @"
        INSERT INTO attribute_set_items
        (set_id, key, value_hash, value_type)
        VALUES (@SetId, @Key, @ValueHash, @ValueType)";

    public const string GetEmptySet = @"
        SELECT id 
        FROM attribute_sets 
        WHERE NOT EXISTS (
            SELECT 1 FROM attribute_set_items i 
            WHERE i.set_id = attribute_sets.id
        )
        LIMIT 1";
}