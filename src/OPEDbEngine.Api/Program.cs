using OPEDbEngine.Application.Users;
using OPEDbEngine.Domain.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using StackExchange.Redis;

var builder = WebApplication.CreateBuilder(args);

// gRPC
builder.Services.AddGrpc();
builder.Services.AddGrpcReflection();

// ✅ ADD THESE
var connStr = "Host=pgbouncer;Port=6432;Database=opedb;Username=ope;Password=opepass;Pooling=false;";
builder.Services.AddSingleton(new DbConnectionFactory(connStr));

builder.Services.AddSingleton<IConnectionMultiplexer>(
    ConnectionMultiplexer.Connect("localhost:6379,abortConnect=false"));

builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddScoped<GetUserUseCase>();
builder.Services.AddScoped<CreateUserUseCase>();

var app = builder.Build();

app.MapGet("/", () => "gRPC server is running");

if (app.Environment.IsDevelopment())
{
    app.MapGrpcReflectionService();
}

app.MapGrpcService<HealthService>();

// ✅ ADD THIS
app.MapGrpcService<UserService>();

app.Run();