using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.Claiming
{
    public interface IClaimService
    {
        Task ClaimNodeAsync(Guid nodeId, Guid sessionId);
        Task ReleaseNodeAsync(Guid nodeId, Guid sessionId);
        Task ForceReleaseAsync(Guid nodeId, Guid sessionId, string reason);
    }
}
