using OPEDbEngine.Core.Models;
using System.Data;

namespace OPEDbEngine.Core.Interfaces
{
    public interface IClaimService
    {
        Task ClaimNodeAsync(Guid nodeId, Guid sessionId);
        Task ValidateClaimAsync(Guid nodeId, Guid sessionId, IDbConnection conn, IDbTransaction tx);
    }
}
