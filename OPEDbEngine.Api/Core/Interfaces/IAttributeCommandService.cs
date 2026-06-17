using OPEDbEngine.Core.Models;

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
            Guid sessionId);

        Task<Guid> BulkSetAttributesAsync(
            Guid nodeId,
            Guid expectedVersionId,
            IEnumerable<AttributeItem> items,
            Guid sessionId);
    }
}