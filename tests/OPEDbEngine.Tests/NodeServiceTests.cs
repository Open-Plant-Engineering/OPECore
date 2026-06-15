using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.Nodes;
using OPEDbEngine.Infrastructure.Service.Versioning;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Tests
{
    public class NodeServiceTests
    {
        [Fact]
        public async Task Should_Create_Node_With_Initial_Version()
        {
            var db = TestDbFactory.Create();

            var attrService = new AttributeSetService(db);
            var versionService = new VersionService(db);
            var nodeService = new NodeService(db, attrService, versionService);

            var nodeId = Guid.NewGuid();
            var sessionId = Guid.NewGuid();

            var versionId = await nodeService.CreateNodeAsync(
                nodeId,
                "PIPE",
                "PIPING",
                sessionId);

            versionId.Should().NotBe(Guid.Empty);

            using var conn = db.Create();

            var node = await conn.QueryFirstAsync(
                "SELECT current_version_id FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            ((Guid)node.current_version_id).Should().Be(versionId);
        }

        [Fact]
        public async Task Should_Reject_Duplicate_Node()
        {
            var db = TestDbFactory.Create();

            var attrService = new AttributeSetService(db);
            var versionService = new VersionService(db);
            var nodeService = new NodeService(db, attrService, versionService);

            var nodeId = Guid.NewGuid();
            var sessionId = Guid.NewGuid();

            await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", sessionId);

            var act = async () =>
                await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", sessionId);

            await act.Should().ThrowAsync<InvalidOperationException>();
        }

        [Fact]
        public async Task Node_Should_Always_Have_Version()
        {
            var db = TestDbFactory.Create();

            var attrService = new AttributeSetService(db);
            var versionService = new VersionService(db);
            var nodeService = new NodeService(db, attrService, versionService);

            var nodeId = Guid.NewGuid();
            var sessionId = Guid.NewGuid();

            await nodeService.CreateNodeAsync(nodeId, "VALVE", "PIPING", sessionId);

            using var conn = db.Create();

            var version = await conn.ExecuteScalarAsync<Guid?>(
                "SELECT current_version_id FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            version.Should().NotBeNull();
        }
    }
}
