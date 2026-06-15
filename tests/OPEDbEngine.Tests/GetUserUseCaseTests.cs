using Xunit;
using Moq;
using FluentAssertions;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

public class GetUserUseCaseTests
{
    [Fact]
    public async Task Should_Return_User_When_Exists()
    {
        // Arrange
        var userId = Guid.NewGuid();

        var mockRepo = new Mock<IUserRepository>();
        mockRepo.Setup(x => x.GetByIdAsync(userId))
                .ReturnsAsync(new User
                {
                    Id = userId,
                    Name = "Test",
                    Email = "test@test.com"
                });

        var useCase = new GetUserUseCase(mockRepo.Object);

        // Act
        var result = await useCase.Execute(userId);

        // Assert
        result.Should().NotBeNull();
        result!.Name.Should().Be("Test");
    }
}