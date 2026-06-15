using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Service.Claiming;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace OPEDbEngine.Tests
{
    public class ClaimServiceTests
    {
        [Fact]
        public async Task Should_Claim_Node()
        {
            var db = TestDbFactory.Create();
            var service = new ClaimService(db);

            var nodeId = Guid.NewGuid();
            var sessionId = Guid.NewGuid();

            using var conn = db.Create();

            await conn.ExecuteAsync(
                "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
                new { Id = nodeId });

            await service.ClaimNodeAsync(nodeId, sessionId);
        }

        [Fact]
        public async Task Should_Reject_When_Already_Claimed()
        {
            var db = TestDbFactory.Create();
            var service = new ClaimService(db);

            var nodeId = Guid.NewGuid();

            using var conn = db.Create();

            await conn.ExecuteAsync(
                "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
                new { Id = nodeId });

            await service.ClaimNodeAsync(nodeId, Guid.NewGuid());

            var act = async () => await service.ClaimNodeAsync(nodeId, Guid.NewGuid());

            await act.Should().ThrowAsync<InvalidOperationException>();
        }

        [Fact]
        public async Task Should_Release_Node()
        {
            var db = TestDbFactory.Create();
            var service = new ClaimService(db);

            var nodeId = Guid.NewGuid();
            var sessionId = Guid.NewGuid();

            using var conn = db.Create();

            await conn.ExecuteAsync(
                "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
                new { Id = nodeId });

            await service.ClaimNodeAsync(nodeId, sessionId);
            await service.ReleaseNodeAsync(nodeId, sessionId);
        }

        [Fact]
        public async Task Should_Reject_Release_By_Other_User()
        {
            var db = TestDbFactory.Create();
            var service = new ClaimService(db);

            var nodeId = Guid.NewGuid();

            using var conn = db.Create();

            await conn.ExecuteAsync(
                "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
                new { Id = nodeId });

            await service.ClaimNodeAsync(nodeId, Guid.NewGuid());

            var act = async () =>
                await service.ReleaseNodeAsync(nodeId, Guid.NewGuid());

            await act.Should().ThrowAsync<InvalidOperationException>();
        }

        [Fact]
        public async Task Should_Force_Release()
        {
            var db = TestDbFactory.Create();
            var service = new ClaimService(db);

            var nodeId = Guid.NewGuid();

            using var conn = db.Create();

            await conn.ExecuteAsync(
                "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
                new { Id = nodeId });

            await service.ClaimNodeAsync(nodeId, Guid.NewGuid());

            await service.ForceReleaseAsync(nodeId, Guid.NewGuid(), "Admin cleanup");
        }
    }
}
