using FluentAssertions;
using OPEDbEngine.Infrastructure.Service.AttributeSets;
using OPEDbEngine.Infrastructure.Service.AttributeSets.Models;
using OPEDbEngine.Infrastructure.Service.Hashing;
using Xunit;

public class AttributeSetServiceTests
{
    private readonly IHashService _hash = new HashService();

    [Fact]
    public async Task Same_Set_Should_Be_Reused()
    {
        var db = TestDbFactory.Create();
        var service = new AttributeSetService(db);

        var valueHash = _hash.HashString("CS");

        var changes = new[]
        {
            new AttributeItem
            {
                Key = 1,
                ValueHash = valueHash,
                ValueType = 1
            }
        };

        var set1 = await service.BuildAttributeSetAsync(null, changes);
        var set2 = await service.BuildAttributeSetAsync(null, changes);

        set1.Should().Be(set2);
    }

    [Fact]
    public async Task Changing_Value_Should_Create_New_Set()
    {
        var db = TestDbFactory.Create();
        var service = new AttributeSetService(db);

        var hash1 = _hash.HashString("CS");
        var hash2 = _hash.HashString("SS");

        var set1 = await service.BuildAttributeSetAsync(null, new[]
        {
            new AttributeItem { Key = 1, ValueHash = hash1, ValueType = 1 }
        });

        var set2 = await service.BuildAttributeSetAsync(set1, new[]
        {
            new AttributeItem { Key = 1, ValueHash = hash2, ValueType = 1 }
        });

        set1.Should().NotBe(set2);
    }

    [Fact]
    public async Task Unchanged_Attributes_Should_Be_Reused()
    {
        var db = TestDbFactory.Create();
        var service = new AttributeSetService(db);

        var hash = _hash.HashString("CS");

        var set1 = await service.BuildAttributeSetAsync(null, new[]
        {
            new AttributeItem { Key = 1, ValueHash = hash, ValueType = 1 }
        });

        // no change
        var set2 = await service.BuildAttributeSetAsync(set1, new AttributeItem[0]);

        set1.Should().Be(set2);
    }
}