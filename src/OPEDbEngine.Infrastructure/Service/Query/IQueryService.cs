using OPEDbEngine.Infrastructure.Service.Query.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.Query
{
    public interface IQueryService
    {
        Task<NodeDto> GetNodeAsync(Guid nodeId);
        Task<NodeDto> GetNodeVersionAsync(Guid nodeId, Guid versionId);
    }
}
