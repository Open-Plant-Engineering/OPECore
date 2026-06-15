using Xunit;
using Moq;
using FluentAssertions;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

using OPEDbEngine.Infrastructure.Service.Hashing;

public class HashServiceTests
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
        var h1 = _hash.HashNumber(100);
        var h2 = _hash.HashNumber(100);

        h1.Should().Equal(h2);
    }
}