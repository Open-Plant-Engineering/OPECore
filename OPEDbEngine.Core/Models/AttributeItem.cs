namespace OPEDbEngine.Core.Models
{
    public class AttributeItem
    {
        public int Key { get; set; }

        public byte[] ValueHash { get; set; } = default!;

        public short ValueType { get; set; }
    }
}