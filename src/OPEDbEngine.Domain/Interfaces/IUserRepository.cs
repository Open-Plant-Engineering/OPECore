using OPEDbEngine.Domain.Entities;

namespace OPEDbEngine.Domain.Interfaces;

public interface IUserRepository
{
    Task<User?> GetByIdAsync(Guid id);
}