using OPEDbEngine.Api.Services;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Core.Interfaces;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("Default");

builder.Services.AddSingleton(new DbConnectionFactory(connectionString!));

builder.Services.AddScoped<IAttributeSetService, AttributeSetService>();
builder.Services.AddScoped<IVersionService, VersionService>();
builder.Services.AddScoped<IQueryService, QueryService>();
builder.Services.AddScoped<INodeService, NodeService>();
builder.Services.AddScoped<IAttributeCommandService, AttributeCommandService>();

// Add services to the container.
builder.Services.AddGrpc();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.MapGrpcService<GreeterService>();
app.MapGrpcService<NodeGrpcService>();

app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
