using Grpc.Core;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Contracts;

public class UserService : User.UserBase
{
    private readonly GetUserUseCase _useCase;

    public UserService(GetUserUseCase useCase)
    {
        _useCase = useCase;
    }

    public override async Task<GetUserResponse> GetUser(GetUserRequest request, ServerCallContext context)
    {
        var user = await _useCase.Execute(Guid.Parse(request.Id));

        if (user == null)
            throw new RpcException(new Status(StatusCode.NotFound, "User not found"));

        return new GetUserResponse
        {
            Id = user.Id.ToString(),
            Name = user.Name,
            Email = user.Email
        };
    }
}