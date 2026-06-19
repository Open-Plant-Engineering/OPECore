namespace OPEDbEngine.Core.DTOs
{
    public class AttributeDto
    {
        public int Key { get; set; }
        public short ValueType { get; set; }
        public object? Value { get; set; }
    }

    public class NodeDto
    {
        public Guid NodeId { get; set; }
        public Guid VersionId { get; set; }
        public string Type { get; set; } = default!;
        public string Owner { get; set; } = default!;
        public List<AttributeDto> Attributes { get; set; } = new();
    }
}