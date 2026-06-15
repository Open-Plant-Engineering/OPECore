using Xunit;
using Moq;
using FluentAssertions;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

public class GetUserUseCaseTests
{
    [Fact]
    public async Task Should_Return_User_When_Found()
    {
        // Arrange
        var id = Guid.NewGuid();

        var mockRepo = new Mock<IUserRepository>();
        mockRepo.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync(new User
            {
                Id = id,
                Name = "Atul",
                Email = "atul@test.com"
            });

        var useCase = new GetUserUseCase(mockRepo.Object);

        // Act
        var result = await useCase.Execute(id);

        // Assert
        result.Should().NotBeNull();
        result!.Email.Should().Be("atul@test.com");
    }

    [Fact]
    public async Task Should_Return_Null_When_User_Not_Found()
    {
        // Arrange
        var id = Guid.NewGuid();

        var mockRepo = new Mock<IUserRepository>();
        mockRepo.Setup(x => x.GetByIdAsync(id))
            .ReturnsAsync((User?)null);

        var useCase = new GetUserUseCase(mockRepo.Object);

        // Act
        var result = await useCase.Execute(id);

        // Assert
        result.Should().BeNull();
    }
}