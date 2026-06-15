using Grpc.Core;
using OPEDbEngine.Application.Users;
using OPEDbEngine.Contracts;

public class UserService : User.UserBase
{
    private readonly GetUserUseCase _useCase;
    private readonly CreateUserUseCase _createUseCase;

    public UserService(GetUserUseCase useCase, CreateUserUseCase createUseCase)
    {
        _useCase = useCase;
        _createUseCase = createUseCase;
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

    public override async Task<CreateUserResponse> CreateUser(CreateUserRequest request, ServerCallContext context)
    {
        var id = await _createUseCase.Execute(request.Name, request.Email);

        return new CreateUserResponse
        {
            Id = id.ToString()
        };
    }
}