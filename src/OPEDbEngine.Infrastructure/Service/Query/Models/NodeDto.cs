using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.Query.Models
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
