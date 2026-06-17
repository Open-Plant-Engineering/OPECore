using OPEDbEngine.Core.Models;
using System.Data;

namespace OPEDbEngine.Core.Interfaces
{
    public interface IAttributeSetService
    {
        Task<Guid> BuildAttributeSetAsync(
            Guid? existingSetId,
            IEnumerable<AttributeItem> changes,
            IDbConnection conn,
            IDbTransaction tx);

        Task<Guid> GetOrCreateEmptySetAsync(
            IDbConnection conn,
            IDbTransaction tx);
    }
}