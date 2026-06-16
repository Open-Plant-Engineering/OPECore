using FluentAssertions;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using Xunit;

[assembly: CollectionBehavior(DisableTestParallelization = true)]
public class AttributeSetTests: IClassFixture<DbFixture>
{
    private AttributeSetService CreateService(out DbConnectionFactory db)
    {
        db = new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

        return new AttributeSetService();
    }

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
}
