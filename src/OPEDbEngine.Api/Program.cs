var builder = WebApplication.CreateBuilder(args);

// Add gRPC services
builder.Services.AddGrpc();

builder.Services.AddGrpcReflection();

var app = builder.Build();

// Optional HTTP endpoint
app.MapGet("/", () => "gRPC server is running");

if (app.Environment.IsDevelopment())
{
    app.MapGrpcReflectionService();
}

app.MapGrpcService<HealthService>();

app.Run();