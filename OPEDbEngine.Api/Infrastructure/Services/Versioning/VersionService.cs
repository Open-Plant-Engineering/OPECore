using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
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
            // ✅ DOMAIN OBJECT INTRODUCED
            var version = new Core.Models.Version
            {
                Id = Guid.NewGuid(),
                NodeId = nodeId,
                ParentVersionId = expectedVersionId,
                AttributeSetId = attributeSetId
            };

            await conn.ExecuteAsync(
                VersionSql.InsertVersion,
                new
                {
                    Id = version.Id,
                    NodeId = version.NodeId,
                    Parent = version.ParentVersionId,
                    AttrSet = version.AttributeSetId,
                    Session = sessionId
                },
                tx);

            var rows = await conn.ExecuteAsync(
                VersionSql.UpdateNodeVersion,
                new
                {
                    Version = version.Id,
                    NodeId = version.NodeId,
                    Expected = expectedVersionId
                },
                tx);

            if (rows != 1)
                throw new InvalidOperationException("Version mismatch.");

            return version.Id;
        }
    }
}
