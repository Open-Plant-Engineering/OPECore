using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Claiming;
using Xunit;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;

public class ClaimServiceTests : IClassFixture<DbFixture>
{
    private DbConnectionFactory CreateDb()
    {
        return new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");
    }

    // ✅ 1. Should claim node
    [Fact]
    public async Task Should_Claim_Node()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, sessionId, conn, tx);

        tx.Commit();

        var claimed = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT claimed_by FROM node_claims WHERE node_id = @Id",
            new { Id = nodeId });

        claimed.Should().Be(sessionId);
    }

    // ✅ 2. Should reject duplicate claim
    [Fact]
    public async Task Should_Reject_When_Already_Claimed()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session1 = Guid.NewGuid();
        var session2 = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, session1, conn, tx);

        var act = async () => 
            await service.ClaimNodeAsync(nodeId, session2, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*already claimed*");

        tx.Rollback();
    }

    // ✅ 3. Should validate correct claim
    [Fact]
    public async Task Should_Validate_Correct_Claim()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, sessionId, conn, tx);

        var act = async () =>
            await service.ValidateClaimAsync(nodeId, sessionId, conn, tx);

        await act.Should().NotThrowAsync();

        tx.Commit();
    }

    // ✅ 4. Should reject wrong session
    [Fact]
    public async Task Should_Reject_When_Claimed_By_Other_Session()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var ownerSession = Guid.NewGuid();
        var otherSession = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, ownerSession, conn, tx);

        var act = async () =>
            await service.ValidateClaimAsync(nodeId, otherSession, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");

        tx.Rollback();
    }

    // ✅ 5. Should reject when no claim exists
    [Fact]
    public async Task Should_Reject_When_No_Claim_Exists()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        var act = async () =>
            await service.ValidateClaimAsync(nodeId, sessionId, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not claimed*");

        tx.Rollback();
    }

    // ✅ 6. Should release node
    [Fact]
    public async Task Should_Release_Node()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var session = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, session, conn, tx);
        await service.ReleaseNodeAsync(nodeId, session, conn, tx);

        tx.Commit();

        var claim = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT claimed_by FROM node_claims WHERE node_id = @Id",
            new { Id = nodeId });

        claim.Should().BeNull();
    }

    // ✅ 7. Should reject release by non-owner
    [Fact]
    public async Task Should_Reject_Release_By_Other_User()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var owner = Guid.NewGuid();
        var other = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, owner, conn, tx);

        var act = async () =>
            await service.ReleaseNodeAsync(nodeId, other, conn, tx);

        await act.Should()
            .ThrowAsync<InvalidOperationException>()
            .WithMessage("*not owner*");

        tx.Rollback();
    }

    // ✅ 8. Should force release
    [Fact]
    public async Task Should_Force_Release()
    {
        var db = CreateDb();
        var service = new ClaimService(db, new ClaimRepository());

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var nodeId = Guid.NewGuid();
        var owner = Guid.NewGuid();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id,'PIPE','PIPING')",
            new { Id = nodeId }, tx);

        await service.ClaimNodeAsync(nodeId, owner, conn, tx);

        await service.ForceReleaseAsync(nodeId, Guid.NewGuid(), "admin cleanup", conn, tx);

        tx.Commit();

        var claim = await conn.ExecuteScalarAsync<Guid?>(
            "SELECT claimed_by FROM node_claims WHERE node_id = @Id",
            new { Id = nodeId });

        claim.Should().BeNull();
    }
}