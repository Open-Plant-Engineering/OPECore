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

}