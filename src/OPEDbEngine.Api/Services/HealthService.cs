using Grpc.Core;
using OPEDbEngine.Contracts;

public class HealthService : Health.HealthBase
{
    public override Task<HealthResponse> Check(HealthRequest request, ServerCallContext context)
    {
        return Task.FromResult(new HealthResponse
        {
            Status = "Healthy"
        });
    }
}