using FluentAssertions;
using OPEDbEngine.Infrastructure.Service.Attributes;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.Claiming;
using OPEDbEngine.Infrastructure.Service.Hashing;
using OPEDbEngine.Infrastructure.Service.Nodes;
using OPEDbEngine.Infrastructure.Service.Query;
using OPEDbEngine.Infrastructure.Service.ValueStore;
using OPEDbEngine.Infrastructure.Service.Versioning;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Tests
{
    public class QueryServiceTests
    {
        [Fact]
        public async Task Should_Get_Node_With_Attributes()
        {
            var db = TestDbFactory.Create();

            var hashService = new HashService();
            var valueStore = new ValueStoreService(db, hashService);

            var attrSet = new AttributeSetService(db);
            var version = new VersionService(db);
            var claim = new ClaimService(db);
            var command = new AttributeCommandService(db, attrSet, version);
            var nodeService = new NodeService(db, attrSet, version);
            var query = new QueryService(db);

            var nodeId = Guid.NewGuid();
            var session = Guid.NewGuid();

            // ✅ Create node
            var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

            // ✅ Claim node
            await claim.ClaimNodeAsync(nodeId, session);

            // ✅ Store value in CAS
            var hash100 = await valueStore.StoreNumberAsync(100d);

            // ✅ Set attribute
            var v2 = await command.SetAttributeAsync(
                nodeId,
                v1,
                1,
                hash100,
                2,
                session);

            // ✅ Query
            var node = await query.GetNodeAsync(nodeId);

            node.NodeId.Should().Be(nodeId);
            node.VersionId.Should().Be(v2);

            node.Attributes.Should().ContainSingle(a =>
                a.Key == 1 &&
                (double)a.Value! == 100d);
        }

        [Fact]
        public async Task Should_Get_Old_Version_Data()
        {
            var db = TestDbFactory.Create();

            var hashService = new HashService();
            var valueStore = new ValueStoreService(db, hashService);

            var attrSet = new AttributeSetService(db);
            var version = new VersionService(db);
            var claim = new ClaimService(db);
            var command = new AttributeCommandService(db, attrSet, version);
            var nodeService = new NodeService(db, attrSet, version);
            var query = new QueryService(db);

            var nodeId = Guid.NewGuid();
            var session = Guid.NewGuid();

            // ✅ Create node
            var v1 = await nodeService.CreateNodeAsync(nodeId, "PIPE", "PIPING", session);

            // ✅ Claim node
            await claim.ClaimNodeAsync(nodeId, session);

            // ✅ Store values
            var hash100 = await valueStore.StoreNumberAsync(100d);
            var hash200 = await valueStore.StoreNumberAsync(200d);

            // ✅ Create versions
            var v2 = await command.SetAttributeAsync(
                nodeId, v1, 1, hash100, 2, session);

            var v3 = await command.SetAttributeAsync(
                nodeId, v2, 1, hash200, 2, session);

            // ✅ Query OLD version
            var old = await query.GetNodeVersionAsync(nodeId, v2);

            old.Attributes.Should().ContainSingle(a =>
                a.Key == 1 &&
                (double)a.Value! == 100d);
        }
    }
}
