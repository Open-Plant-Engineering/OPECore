namespace OPEDbEngine.Infrastructure.Models;

public class NodeRow
{
    public Guid Id { get; set; }
    public string Type { get; set; } = default!;
    public string Owner { get; set; } = default!;
    public Guid? current_version_id { get; set; }
}

public class NodeMeta
{
    public string Type { get; set; } = default!;
    public string Owner { get; set; } = default!;
}