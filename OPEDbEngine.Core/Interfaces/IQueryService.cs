using OPEDbEngine.Core.DTOs;

namespace OPEDbEngine.Core.Interfaces
{
    public interface IQueryService
    {
        Task<NodeDto> GetNodeAsync(Guid nodeId);
        Task<NodeDto> GetNodeVersionAsync(Guid nodeId, Guid versionId);
    }
}
