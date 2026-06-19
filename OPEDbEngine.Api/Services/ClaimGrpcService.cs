using Grpc.Core;
using ClaimGrpc = OPEDbEngine.gRPC.Claim;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;

namespace OPEDbEngine.Api.Services
{
    public class ClaimGrpcService : ClaimGrpc.ClaimService.ClaimServiceBase
    {
        private readonly IClaimService _claimService;
        private readonly DbConnectionFactory _db;

        public ClaimGrpcService(IClaimService claimService, DbConnectionFactory db)
        {
            _claimService = claimService;
            _db = db;
        }

        // ✅ STREAM CLAIM
        public override async Task StreamClaimNodes(
            IAsyncStreamReader<ClaimGrpc.ClaimNodeRequest> requestStream,
            IServerStreamWriter<ClaimGrpc.ClaimNodeResponse> responseStream,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            await foreach (var req in requestStream.ReadAllAsync())
            {
                using var tx = conn.BeginTransaction();

                try
                {
                    var nodeId = Guid.Parse(req.NodeId);
                    var sessionId = Guid.Parse(req.SessionId);

                    await _claimService.ClaimNodeAsync(
                        nodeId,
                        sessionId,
                        conn,
                        tx);

                    tx.Commit();

                    await responseStream.WriteAsync(new ClaimGrpc.ClaimNodeResponse
                    {
                        NodeId = req.NodeId,
                        Success = true,
                        Message = "Claimed successfully"
                    });
                }
                catch (Exception ex)
                {
                    tx.Rollback();

                    await responseStream.WriteAsync(new ClaimGrpc.ClaimNodeResponse
                    {
                        NodeId = req.NodeId,
                        Success = false,
                        Message = ex.Message
                    });
                }
            }
        }

        // ✅ STREAM RELEASE
        public override async Task StreamReleaseNodes(
            IAsyncStreamReader<ClaimGrpc.ReleaseNodeRequest> requestStream,
            IServerStreamWriter<ClaimGrpc.ReleaseNodeResponse> responseStream,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            await foreach (var req in requestStream.ReadAllAsync())
            {
                using var tx = conn.BeginTransaction();

                try
                {
                    var nodeId = Guid.Parse(req.NodeId);
                    var sessionId = Guid.Parse(req.SessionId);

                    await _claimService.ReleaseNodeAsync(
                        nodeId,
                        sessionId,
                        conn,
                        tx);

                    tx.Commit();

                    await responseStream.WriteAsync(new ClaimGrpc.ReleaseNodeResponse
                    {
                        NodeId = req.NodeId,
                        Success = true,
                        Message = "Released successfully"
                    });
                }
                catch (Exception ex)
                {
                    tx.Rollback();

                    await responseStream.WriteAsync(new ClaimGrpc.ReleaseNodeResponse
                    {
                        NodeId = req.NodeId,
                        Success = false,
                        Message = ex.Message
                    });
                }
            }
        }
    }
}