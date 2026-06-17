namespace OPEDbEngine.Core.Models
{
    public class Claim
    {
        public Guid NodeId { get; set; }
        public Guid ClaimedBy { get; set; }
    }

    public class AttributeItem
    {
        public int Key { get; set; }

        public byte[] ValueHash { get; set; } = default!;

        public short ValueType { get; set; }
    }

    public class Node
    {
        public Guid Id { get; set; }
        public string Type { get; set; } = default!;
        public string Owner { get; set; } = default!;
    }

    public class Version
    {
        public Guid Id { get; set; }
        public Guid NodeId { get; set; }
        public Guid? ParentVersionId { get; set; }
        public Guid AttributeSetId { get; set; }
    }
}
