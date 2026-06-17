using OPEDbEngine.Api.Services;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.AttributeSets;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Versioning;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.Claiming;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Hashing;
using OPEDbEngine.Infrastructure.Repositories;

var builder = WebApplication.CreateBuilder(args);

var connectionString = builder.Configuration.GetConnectionString("Default");

builder.Services.AddSingleton(new DbConnectionFactory(connectionString!));

builder.Services.AddScoped<IAttributeSetService, AttributeSetService>();
builder.Services.AddScoped<IVersionService, VersionService>();
builder.Services.AddScoped<IQueryService, QueryService>();
builder.Services.AddScoped<INodeService, NodeService>();
builder.Services.AddScoped<IAttributeCommandService, AttributeCommandService>();
builder.Services.AddScoped<IClaimService, ClaimService>();
builder.Services.AddScoped<IHashService, HashService>();

builder.Services.AddScoped<AttributeRepository>();
builder.Services.AddScoped<NodeService>();
builder.Services.AddScoped<AttributeCommandService>();
builder.Services.AddScoped<QueryService>();
builder.Services.AddScoped<ValueStoreService>();
builder.Services.AddScoped<NodeRepository>();
builder.Services.AddScoped<VersionRepository>();


// Add services to the container.
builder.Services.AddGrpc();

var app = builder.Build();

// Configure the HTTP request pipeline.
app.MapGrpcService<GreeterService>();
app.MapGrpcService<NodeGrpcService>();

app.MapGet("/", () => "Communication with gRPC endpoints must be made through a gRPC client. To learn how to create a client, visit: https://go.microsoft.com/fwlink/?linkid=2086909");

app.Run();
