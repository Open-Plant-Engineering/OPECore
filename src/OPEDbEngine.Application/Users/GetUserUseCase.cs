using OPEDbEngine.Domain.Entities;
using OPEDbEngine.Domain.Interfaces;

namespace OPEDbEngine.Application.Users;

public class GetUserUseCase
{
    private readonly IUserRepository _repo;

    public GetUserUseCase(IUserRepository repo)
    {
        _repo = repo;
    }

    public async Task<User?> Execute(Guid id)
    {
        return await _repo.GetByIdAsync(id);
    }
}