using System.Data;

namespace OPEDbEngine.Core.Interfaces
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