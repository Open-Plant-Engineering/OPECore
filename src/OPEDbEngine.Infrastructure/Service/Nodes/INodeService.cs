using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.Nodes
{
    public interface INodeService
    {
        Task<Guid> CreateNodeAsync(
            Guid nodeId,
            string type,
            string owner,
            Guid sessionId);
    }
}
