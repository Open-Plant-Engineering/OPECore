using Dapper;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using OPEDbEngine.Infrastructure.Service.Hashing;
using OPEDbEngine.Infrastructure.Service.Versioning;
using Xunit;

public class VersionServiceTests
{
    private readonly IHashService _hash = new HashService();

    [Fact]
    public async Task Should_Create_New_Version()
    {
        var db = TestDbFactory.Create();

        var versionService = new VersionService(db);
        var attributeService = new AttributeSetService(db);

        // Create node manually
        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        using var conn = db.Create();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id, 'PIPE', 'PIPING')",
            new { Id = nodeId });

        var attrSet = await attributeService.BuildAttributeSetAsync(null, new[]
        {
            new AttributeItem
            {
                Key = 1,
                ValueHash = _hash.HashNumber(100),
                ValueType = 2
            }
        });

        // First version
        var v1 = await versionService.CreateVersionAsync(
            nodeId,
            Guid.Empty,
            attrSet,
            sessionId);

        v1.Should().NotBe(Guid.Empty);
    }

    [Fact]
    public async Task Should_Reject_On_Version_Mismatch()
    {
        var db = TestDbFactory.Create();

        var versionService = new VersionService(db);
        var attributeService = new AttributeSetService(db);

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        using var conn = db.Create();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id, 'PIPE', 'PIPING')",
            new { Id = nodeId });

        var attrSet = await attributeService.BuildAttributeSetAsync(null, new[]
        {
            new AttributeItem
            {
                Key = 1,
                ValueHash = _hash.HashNumber(100),
                ValueType = 2
            }
        });

        var v1 = await versionService.CreateVersionAsync(
            nodeId,
            Guid.Empty,
            attrSet,
            sessionId);

        // Wrong expected version
        var act = async () => await versionService.CreateVersionAsync(
            nodeId,
            Guid.NewGuid(),
            attrSet,
            sessionId);

        await act.Should().ThrowAsync<InvalidOperationException>();
    }

    [Fact]
    public async Task Should_Reject_First_Version_When_Expected_Not_Empty()
    {
        var db = TestDbFactory.Create();
        var versionService = new VersionService(db);
        var attributeService = new AttributeSetService(db);

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        using var conn = db.Create();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id, 'PIPE', 'PIPING')",
            new { Id = nodeId });

        var attrSet = await attributeService.BuildAttributeSetAsync(null, new[]
        {
        new AttributeItem
        {
            Key = 1,
            ValueHash = new HashService().HashNumber(100),
            ValueType = 2
        }
    });

        var act = async () => await versionService.CreateVersionAsync(
            nodeId,
            Guid.NewGuid(), // ❌ wrong initial expected
            attrSet,
            sessionId);

        await act.Should().ThrowAsync<InvalidOperationException>();
    }

    [Fact]
    public async Task Should_Reject_When_Node_Does_Not_Exist()
    {
        var db = TestDbFactory.Create();
        var versionService = new VersionService(db);

        var fakeNodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        var attrSetId = Guid.NewGuid();

        var act = async () => await versionService.CreateVersionAsync(
            fakeNodeId,
            Guid.Empty,
            attrSetId,
            sessionId);

        await act.Should().ThrowAsync<InvalidOperationException>();
    }
    [Fact]
    public async Task Should_Reject_Second_Update_With_Same_Version()
    {
        var db = TestDbFactory.Create();
        var versionService = new VersionService(db);
        var attrService = new AttributeSetService(db);
        var hash = new HashService();

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        using var conn = db.Create();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id, 'PIPE', 'PIPING')",
            new { Id = nodeId });

        var attrSet = await attrService.BuildAttributeSetAsync(null, new[]
        {
        new AttributeItem
        {
            Key = 1,
            ValueHash = hash.HashNumber(100),
            ValueType = 2
        }
    });

        // First version
        var v1 = await versionService.CreateVersionAsync(
            nodeId,
            Guid.Empty,
            attrSet,
            sessionId);

        // ✅ valid update
        var v2 = await versionService.CreateVersionAsync(
            nodeId,
            v1,
            attrSet,
            sessionId);

        // ❌ trying again using old v1
        var act = async () => await versionService.CreateVersionAsync(
            nodeId,
            v1,
            attrSet,
            sessionId);

        await act.Should().ThrowAsync<InvalidOperationException>();
    }
    [Fact]
    public async Task Should_Reject_When_AttributeSet_Does_Not_Exist()
    {
        var db = TestDbFactory.Create();
        var versionService = new VersionService(db);

        var nodeId = Guid.NewGuid();
        var sessionId = Guid.NewGuid();

        using var conn = db.Create();

        await conn.ExecuteAsync(
            "INSERT INTO nodes (id, type, owner) VALUES (@Id, 'PIPE', 'PIPING')",
            new { Id = nodeId });

        var fakeSet = Guid.NewGuid();

        var act = async () => await versionService.CreateVersionAsync(
            nodeId,
            Guid.Empty,
            fakeSet,
            sessionId);

        await act.Should().ThrowAsync<InvalidOperationException>();
    }


}