using System.Data;

namespace OPEDbEngine.Core.Interfaces
{
    public interface IVersionService
    {
        Task<Guid> CreateVersionAsync(
            Guid nodeId,
            Guid expectedVersionId,
            Guid attributeSetId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx);
    }
}
