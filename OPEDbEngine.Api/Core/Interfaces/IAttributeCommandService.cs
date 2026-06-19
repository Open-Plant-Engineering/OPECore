using OPEDbEngine.Core.Models;
using System.Data;

namespace OPEDbEngine.Core.Interfaces
{
    public interface IAttributeCommandService
    {
        Task<Guid> SetAttributeAsync(
            Guid nodeId,
            Guid expectedVersionId,
            int key,
            byte[] valueHash,
            short valueType,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx);

        Task<Guid> BulkSetAttributesAsync(
            Guid nodeId,
            Guid expectedVersionId,
            IEnumerable<AttributeItem> items,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx);

        Task<Guid> RemoveAttributesAsync(
            Guid nodeId,
            Guid expectedVersionId,
            IEnumerable<int> keys,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx);

        Task<Guid> RemoveAttributeAsync(
            Guid nodeId,
            Guid expectedVersionId,
            int key,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx);
        
    }
}