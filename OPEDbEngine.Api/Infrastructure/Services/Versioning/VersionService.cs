using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;
using OPEDbEngine.Infrastructure.Sql;

namespace OPEDbEngine.Infrastructure.Services.Versioning
{
    public class VersionService : IVersionService
    {
        private readonly VersionRepository _versionRepo;

        public VersionService(VersionRepository versionRepo)
        {
            _versionRepo = versionRepo;
        }

        public async Task<Guid> CreateVersionAsync(
            Guid nodeId,
            Guid expectedVersionId,
            Guid attributeSetId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {

            var newVersionId = Guid.NewGuid();

            // ✅ Insert new version
            await conn.ExecuteAsync(
                VersionSql.InsertVersion,
                new
                {
                    Id = newVersionId,
                    NodeId = nodeId,
                    Parent = expectedVersionId,   // ✅ TRUST caller
                    AttrSet = attributeSetId,
                    Session = sessionId
                },
                tx);

            // ✅ Update node pointer
            var rows = await conn.ExecuteAsync(
                VersionSql.UpdateNodeVersion,   // ✅ OCC check here
                new
                {
                    Version = newVersionId,
                    NodeId = nodeId,
                    Expected = expectedVersionId
                },
                tx);

            // ✅ Ensure exactly one row updated
            if (rows != 1)
                throw new InvalidOperationException("Version mismatch.");

            return newVersionId;
        }
    }
}