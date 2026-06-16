namespace OPEDbEngine.Core.DTOs
{
    public class AttributeDto
    {
        public int Key { get; set; }
        public short ValueType { get; set; }
        public object? Value { get; set; }
    }
}