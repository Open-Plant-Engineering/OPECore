using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

namespace OPEDbEngine.Application.Users;

public class CreateUserUseCase
{
    private readonly IUserRepository _repo;

    public CreateUserUseCase(IUserRepository repo)
    {
        _repo = repo;
    }

    public async Task<Guid> Execute(string name, string email)
    {
        var user = new User
        {
            Id = Guid.NewGuid(),
            Name = name,
            Email = email
        };

        return await _repo.CreateAsync(user);
    }
}
