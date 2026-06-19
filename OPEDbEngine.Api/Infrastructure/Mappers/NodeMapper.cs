using OPEDbEngine.Infrastructure.Models;
using OPEDbEngine.Core.Models;

namespace OPEDbEngine.Infrastructure.Mappers
{
    public static class NodeMapper
    {
        public static Node ToDomain(NodeRow row)
        {
            return new Node
            {
                Id = row.Id,
                Type = row.Type,
                Owner = row.Owner
            };
        }

        public static Node ToDomain(NodeMeta row)
        {
            return new Node
            {
                Id = row.Id,
                Type = row.Type,
                Owner = row.Owner
            };
        }
    }
}
