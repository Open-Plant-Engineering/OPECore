using OPEDbEngine.Core.DTOs;
using System.Data;

namespace OPEDbEngine.Core.Interfaces
{
    public interface IQueryService
    {
        Task<NodeDto> GetNodeAsync(
            Guid nodeId,
            IDbConnection conn,
            IDbTransaction? tx = null);

        Task<NodeDto> GetNodeVersionAsync(
            Guid nodeId, 
            Guid versionId,
            IDbConnection conn,
            IDbTransaction? tx = null);
    }
}
