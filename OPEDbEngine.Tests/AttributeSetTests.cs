using FluentAssertions;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using Xunit;
using OPEDbEngine.Infrastructure.Repositories;

public class AttributeSetTests : IClassFixture<DbFixture>
{
    private AttributeSetService CreateService(out DbConnectionFactory db)
    {
        db = new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

        var AttributeRepo = new AttributeRepository();
        return new AttributeSetService(AttributeRepo);
    }

    // ✅ 1. Identical set reuse
    [Fact]
    public async Task Should_Reuse_Identical_Attribute_Set()
    {
        var service = CreateService(out var db);

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var item = new AttributeItem
        {
            Key = 1,
            ValueHash = new byte[] { 1, 2, 3 },
            ValueType = 2
        };

        var set1 = await service.BuildAttributeSetAsync(null, new[] { item }, conn, tx);
        var set2 = await service.BuildAttributeSetAsync(null, new[] { item }, conn, tx);

        set1.Should().Be(set2);

        tx.Commit();
    }

    // ✅ 2. Changing value creates new set
    [Fact]
    public async Task Should_Create_New_Set_When_Value_Changes()
    {
        var service = CreateService(out var db);

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var item1 = new AttributeItem
        {
            Key = 1,
            ValueHash = new byte[] { 1, 2, 3 },
            ValueType = 2
        };

        var item2 = new AttributeItem
        {
            Key = 1,
            ValueHash = new byte[] { 9, 9, 9 },
            ValueType = 2
        };

        var set1 = await service.BuildAttributeSetAsync(null, new[] { item1 }, conn, tx);

        var set2 = await service.BuildAttributeSetAsync(set1, new[] { item2 }, conn, tx);

        set1.Should().NotBe(set2);

        tx.Commit();
    }

    // ✅ 3. No changes → reuse existing set
    [Fact]
    public async Task Should_Reuse_Set_When_No_Changes_Are_Applied()
    {
        var service = CreateService(out var db);

        using var conn = db.Create();
        conn.Open();
        using var tx = conn.BeginTransaction();

        var item = new AttributeItem
        {
            Key = 1,
            ValueHash = new byte[] { 1, 2, 3 },
            ValueType = 2
        };

        var set1 = await service.BuildAttributeSetAsync(null, new[] { item }, conn, tx);

        // ✅ no changes
        var set2 = await service.BuildAttributeSetAsync(set1, Enumerable.Empty<AttributeItem>(), conn, tx);

        set1.Should().Be(set2);

        tx.Commit();
    }
}
