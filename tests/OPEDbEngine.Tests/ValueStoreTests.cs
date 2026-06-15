using Xunit;
using Moq;
using FluentAssertions;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

using OPEDbEngine.Infrastructure.Service.Hashing;
using OPEDbEngine.Infrastructure.Service.ValueStore;

public class ValueStoreTests
{
    private readonly IHashService _hash = new HashService();

    [Fact]
    public async Task Same_String_Should_Not_Insert_Twice()
    {
        var db = TestDbFactory.Create();

        await TestDbFactory.ResetAsync(); // ✅ clean state

        var service = new ValueStoreService(db, _hash);

        var h1 = await service.StoreStringAsync("CS");
        var h2 = await service.StoreStringAsync("CS");

        h1.Should().Equal(h2);
    }
}
