using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.AttributeSets
{
    public interface IAttributeSetService
    {
        Task<Guid> BuildAttributeSetAsync(
            Guid? existingSetId,
            IEnumerable<AttributeItem> changes);
    }
}
