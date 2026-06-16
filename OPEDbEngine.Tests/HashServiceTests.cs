using Xunit;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Services.Hashing;

public class HashServiceTests: IClassFixture<DbFixture>
{
    private readonly IHashService _hash = new HashService();

    [Fact]
    public void Same_String_Should_Have_Same_Hash()
    {
        var h1 = _hash.HashString("CS");
        var h2 = _hash.HashString("CS");

        h1.Should().Equal(h2);
    }

    [Fact]
    public void Different_String_Should_Have_Different_Hash()
    {
        var h1 = _hash.HashString("CS");
        var h2 = _hash.HashString("SS");

        h1.Should().NotEqual(h2);
    }

    [Fact]
    public void Same_Number_Should_Have_Same_Hash()
    {
        var h1 = _hash.HashNumber(100d);   // ✅ double
        var h2 = _hash.HashNumber(100d);   // ✅ double

        h1.Should().Equal(h2);
    }

    [Fact]
    public void String_And_Number_Should_Not_Have_Same_Hash()
    {
        var strHash = _hash.HashString("100");
        var numHash = _hash.HashNumber(100d);

        strHash.Should().NotEqual(numHash);
    }

}