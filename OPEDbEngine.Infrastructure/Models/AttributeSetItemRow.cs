namespace OPEDbEngine.Infrastructure.Models
{
    public class AttributeSetItemRow
    {
        public Guid SetId { get; set; }
        public int Key { get; set; }
        public byte[] ValueHash { get; set; } = Array.Empty<byte>();
        public short ValueType { get; set; }
    }
}