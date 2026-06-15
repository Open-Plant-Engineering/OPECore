using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.Query.Models
{
    public class AttributeDto
    {
        public int Key { get; set; }
        public short ValueType { get; set; }
        public object? Value { get; set; }
    }
}
