using Xunit;
using FluentAssertions;
using OPEDbEngine.Infrastructure.Services.Hashing;

public class HashServiceTests : IClassFixture<DbFixture>
{
    private readonly IHashService _hash = new HashService();

    // ✅ 1. Same string → same hash
    [Fact]
    public void Same_String_Should_Have_Same_Hash()
    {
        var h1 = _hash.HashString("CS");
        var h2 = _hash.HashString("CS");

        h1.Should().Equal(h2);
    }

    // ✅ 2. Different strings → different hash
    [Fact]
    public void Different_String_Should_Have_Different_Hash()
    {
        var h1 = _hash.HashString("CS");
        var h2 = _hash.HashString("SS");

        h1.Should().NotEqual(h2);
    }

    // ✅ 3. Same number → same hash
    [Fact]
    public void Same_Number_Should_Have_Same_Hash()
    {
        var h1 = _hash.HashNumber(100d);
        var h2 = _hash.HashNumber(100d);

        h1.Should().Equal(h2);
    }

    // ✅ 4. Different numbers → different hash
    [Fact]
    public void Different_Number_Should_Have_Different_Hash()
    {
        var h1 = _hash.HashNumber(100d);
        var h2 = _hash.HashNumber(200d);

        h1.Should().NotEqual(h2);
    }

    // ✅ 5. String vs Number → must differ
    [Fact]
    public void String_And_Number_Should_Not_Have_Same_Hash()
    {
        var strHash = _hash.HashString("100");
        var numHash = _hash.HashNumber(100d);

        strHash.Should().NotEqual(numHash);
    }

    // ✅ 6. Case sensitivity
    [Fact]
    public void Different_Case_Should_Produce_Different_Hash()
    {
        var lower = _hash.HashString("cs");
        var upper = _hash.HashString("CS");

        lower.Should().NotEqual(upper);
    }

    // ✅ 7. Unicode support
    [Fact]
    public void Unicode_String_Should_Be_Hashed_Consistently()
    {
        var h1 = _hash.HashString("π");
        var h2 = _hash.HashString("π");

        h1.Should().Equal(h2);
    }

    // ✅ 8. Empty string
    [Fact]
    public void Empty_String_Should_Produce_Stable_Hash()
    {
        var h1 = _hash.HashString("");
        var h2 = _hash.HashString("");

        h1.Should().Equal(h2);
    }

    // ✅ 9. Negative numbers
    [Fact]
    public void Negative_Number_Should_Have_Stable_Hash()
    {
        var h1 = _hash.HashNumber(-100d);
        var h2 = _hash.HashNumber(-100d);

        h1.Should().Equal(h2);
    }
}