using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Infrastructure.Service.Versioning
{
    public interface IVersionService
    {
        Task<Guid> CreateVersionAsync(
            Guid nodeId,
            Guid expectedVersionId,
            Guid attributeSetId,
            Guid sessionId);
    }

}
