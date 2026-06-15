using FluentAssertions;
using OPEDbEngine.Infrastructure.Service.Attributes;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using OPEDbEngine.Infrastructure.Service.Claiming;
using OPEDbEngine.Infrastructure.Service.Hashing;
using OPEDbEngine.Infrastructure.Service.Nodes;
using OPEDbEngine.Infrastructure.Service.Versioning;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Tests
{
    public class AttributeCommandServiceTests
    {
        [Fact]
        public async Task Should_Set_Attribute()
        {
            var db = TestDbFactory.Create();

            var attrSet = new AttributeSetService(db);
            var version = new VersionService(db);
            var claim = new ClaimService(db);

            var command = new AttributeCommandService(db, attrSet, version);

            var nodeService = new NodeService(db, attrSet, version);

            var nodeId = Guid.NewGuid();
            var session = Guid.NewGuid();

            var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

            await claim.ClaimNodeAsync(nodeId, session);

            var newVersion = await command.SetAttributeAsync(
                nodeId,
                v1,
                1,
                new HashService().HashNumber(100),
                2,
                session);

            newVersion.Should().NotBe(v1);
        }

        [Fact]
        public async Task Should_Reject_Without_Claim()
        {
            var db = TestDbFactory.Create();

            var attrSet = new AttributeSetService(db);
            var version = new VersionService(db);

            var command = new AttributeCommandService(db, attrSet, version);

            var nodeService = new NodeService(db, attrSet, version);

            var nodeId = Guid.NewGuid();
            var session = Guid.NewGuid();

            var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

            var act = async () => await command.SetAttributeAsync(
                nodeId,
                v1,
                1,
                new HashService().HashNumber(100),
                2,
                session);

            await act.Should().ThrowAsync<InvalidOperationException>();
        }

        [Fact]
        public async Task Should_Set_Multiple_Attributes()
        {
            var db = TestDbFactory.Create();

            var attrSet = new AttributeSetService(db);
            var version = new VersionService(db);
            var claim = new ClaimService(db);

            var command = new AttributeCommandService(db, attrSet, version);

            var nodeService = new NodeService(db, attrSet, version);

            var nodeId = Guid.NewGuid();
            var session = Guid.NewGuid();

            var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

            await claim.ClaimNodeAsync(nodeId, session);

            var v2 = await command.BulkSetAttributesAsync(
                nodeId,
                v1,
                new[]
                {
            new AttributeItem { Key = 1, ValueHash = new HashService().HashNumber(100), ValueType = 2 },
            new AttributeItem { Key = 2, ValueHash = new HashService().HashString("CS"), ValueType = 1 }
                },
                session);

            v2.Should().NotBe(v1);
        }

        [Fact]
        public async Task Should_Reject_Version_Mismatch()
        {
            var db = TestDbFactory.Create();

            var attrSetService = new AttributeSetService(db);
            var versionService = new VersionService(db);
            var claimService = new ClaimService(db);

            var commandService = new AttributeCommandService(db, attrSetService, versionService);
            var nodeService = new NodeService(db, attrSetService, versionService);

            var nodeId = Guid.NewGuid();
            var sessionId = Guid.NewGuid();

            // ✅ Create node
            var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", sessionId);

            // ✅ Claim node
            await claimService.ClaimNodeAsync(nodeId, sessionId);

            // ✅ Try update with WRONG version
            var wrongVersion = Guid.NewGuid();

            var act = async () => await commandService.SetAttributeAsync(
                nodeId,
                wrongVersion, // ❌ incorrect version
                1,
                new HashService().HashNumber(100),
                2,
                sessionId);

            await act.Should().ThrowAsync<InvalidOperationException>()
                .WithMessage("*Version mismatch*");
        }
    }
}
