namespace OPEDbEngine.Core.DTOs
{
    public class NodeDto
    {
        public Guid NodeId { get; set; }
        public Guid VersionId { get; set; }
        public string Type { get; set; } = default!;
        public string Owner { get; set; } = default!;
        public List<AttributeDto> Attributes { get; set; } = new();
    }
}