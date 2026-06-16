using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using Xunit;

public class ValueStoreTests : IClassFixture<DbFixture>
{
    private ValueStoreService CreateService()
    {
        var db = new DbConnectionFactory(
            "Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

        return new ValueStoreService(db, new HashService());
    }

    // ✅ 1. Same number → no duplicate insert
    [Fact]
    public async Task Same_Number_Should_Not_Insert_Twice()
    {
        var service = CreateService();

        var h1 = await service.StoreNumberAsync(100d);
        var h2 = await service.StoreNumberAsync(100d);

        h1.Should().Equal(h2);
    }

    // ✅ 2. Same string → no duplicate insert
    [Fact]
    public async Task Same_String_Should_Not_Insert_Twice()
    {
        var service = CreateService();

        var h1 = await service.StoreStringAsync("CS");
        var h2 = await service.StoreStringAsync("CS");

        h1.Should().Equal(h2);
    }

    // ✅ 3. Different numbers → different hashes
    [Fact]
    public async Task Different_Number_Should_Produce_Different_Hash()
    {
        var service = CreateService();

        var h1 = await service.StoreNumberAsync(100d);
        var h2 = await service.StoreNumberAsync(200d);

        h1.Should().NotEqual(h2);
    }

    // ✅ 4. Different strings → different hashes
    [Fact]
    public async Task Different_String_Should_Produce_Different_Hash()
    {
        var service = CreateService();

        var h1 = await service.StoreStringAsync("CS");
        var h2 = await service.StoreStringAsync("SS");

        h1.Should().NotEqual(h2);
    }

    // ✅ 5. String vs number → different hash
    [Fact]
    public async Task String_And_Number_Should_Not_Conflict()
    {
        var service = CreateService();

        var strHash = await service.StoreStringAsync("100");
        var numHash = await service.StoreNumberAsync(100d);

        strHash.Should().NotEqual(numHash);
    }

    // ✅ 6. Repeated inserts remain stable
    [Fact]
    public async Task Repeated_Insert_Should_Return_Same_Hash()
    {
        var service = CreateService();

        var hashes = new List<byte[]>();

        for (int i = 0; i < 5; i++)
        {
            hashes.Add(await service.StoreNumberAsync(100d));
        }

        hashes.Should().AllBeEquivalentTo(hashes[0]);
    }

    // ✅ 7. Negative numbers handled correctly
    [Fact]
    public async Task Negative_Number_Should_Have_Stable_Hash()
    {
        var service = CreateService();

        var h1 = await service.StoreNumberAsync(-100d);
        var h2 = await service.StoreNumberAsync(-100d);

        h1.Should().Equal(h2);
    }
}