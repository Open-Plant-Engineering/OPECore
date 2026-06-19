namespace OPEDbEngine.Infrastructure.Models
{
    public class AttributeSetItemRow
    {
        public Guid SetId { get; set; }
        public int Key { get; set; }
        public byte[] ValueHash { get; set; } = Array.Empty<byte>();
        public short ValueType { get; set; }
    }

    public class AttributeSetRow
    {
        public Guid Id { get; set; }
        public byte[] Hash { get; set; } = default!;
    }

    public class NodeRow
    {
        public Guid Id { get; set; }
        public string Type { get; set; } = default!;
        public string Owner { get; set; } = default!;
        public Guid? Current_version_id { get; set; }
    }

    public class NodeMeta
    {
        public Guid Id { get; set; }
        public string Type { get; set; } = default!;
        public string Owner { get; set; } = default!;
    }

    public class StringValueRow
    {
        public byte[] hash { get; set; } = default!;
        public string value { get; set; } = default!;
    }

    public class NumberValueRow
    {
        public byte[] Hash { get; set; } = default!;
        public double Value { get; set; }
    }

    public class BoolValueRow
    {
        public byte[] Hash { get; set; } = default!;
        public bool Value { get; set; }
    }

    public class ClaimRow
    {
        public Guid Node_id { get; set; }
        public Guid Claimed_by { get; set; }
    }

    public class VersionRow
    {
        public Guid Id { get; set; }
        public Guid Node_id { get; set; }
        public Guid? Parent_version_id { get; set; }
        public Guid Attribute_set_id { get; set; }
        public Guid Created_by { get; set; }
    }
}