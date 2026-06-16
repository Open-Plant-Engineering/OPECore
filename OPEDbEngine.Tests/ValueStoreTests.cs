using FluentAssertions;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using Xunit;

public class ValueStoreTests: IClassFixture<DbFixture>
{
    private ValueStoreService CreateService()
    {
        var db = new DbConnectionFactory("Host=localhost;Port=5432;Database=opedb;Username=ope;Password=opepass");

        return new ValueStoreService(db, new HashService());
    }

    [Fact]
    public async Task Same_Number_Should_Not_Insert_Twice()
    {
        var service = CreateService();

        var h1 = await service.StoreNumberAsync(100d);
        var h2 = await service.StoreNumberAsync(100d);

        h1.Should().Equal(h2);
    }
}