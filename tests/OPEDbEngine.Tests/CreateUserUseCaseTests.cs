using Xunit;
using Moq;
using FluentAssertions;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

public class CreateUserUseCaseTests
{
    [Fact]
    public async Task Should_Create_User_And_Return_Id()
    {
        // Arrange
        var mockRepo = new Mock<IUserRepository>();

        mockRepo.Setup(x => x.CreateAsync(It.IsAny<User>()))
                .ReturnsAsync((User u) => u.Id);

        var useCase = new CreateUserUseCase(mockRepo.Object);

        // Act
        var result = await useCase.Execute("Atul", "atul@test.com");

        // Assert
        result.Should().NotBe(Guid.Empty);

        mockRepo.Verify(x => x.CreateAsync(It.IsAny<User>()), Times.Once);
    }
}
