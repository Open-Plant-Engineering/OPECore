using Grpc.Net.Client;

public class GrpcTestBase
{
    protected GrpcChannel CreateChannel()
    {
        return GrpcChannel.ForAddress("http://localhost:5217"); // adjust if needed
    }
}