using Grpc.Core;
using WorkGrpc = OPEDbEngine.gRPC.Work;
using NodeGrpc = OPEDbEngine.gRPC.Node;

using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;

namespace OPEDbEngine.Api.Services
{
    public class WorkGrpcService : WorkGrpc.WorkService.WorkServiceBase
    {
        private readonly INodeService _nodeService;
        private readonly IAttributeCommandService _attrService;
        private readonly DbConnectionFactory _db;

        public WorkGrpcService(
            INodeService nodeService,
            IAttributeCommandService attrService,
            DbConnectionFactory db)
        {
            _nodeService = nodeService;
            _attrService = attrService;
            _db = db;
        }

        public override async Task StreamSaveChanges(
            IAsyncStreamReader<WorkGrpc.SaveNodeRequest> requestStream,
            IServerStreamWriter<WorkGrpc.SaveNodeResponse> responseStream,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            await foreach (var req in requestStream.ReadAllAsync())
            {
                using var tx = conn.BeginTransaction();

                try
                {
                    string nodeId = "";
                    Guid newVersionId = Guid.Empty;

                    if (req.CreateNode != null)
                    {
                        var r = req.CreateNode;

                        nodeId = r.NodeId;

                        newVersionId = await _nodeService.CreateNodeAsync(
                            Guid.Parse(r.NodeId),
                            r.Type,
                            r.Owner,
                            Guid.Parse(r.SessionId),
                            conn,
                            tx);
                    }
                    else if (req.SetAttribute != null)
                    {
                        var r = req.SetAttribute;

                        nodeId = r.NodeId;

                        newVersionId = await _attrService.SetAttributeAsync(
                            Guid.Parse(r.NodeId),
                            Guid.Parse(r.VersionId),
                            r.Key,
                            r.ValueHash.ToByteArray(),
                            (short)r.ValueType,
                            Guid.Parse(r.SessionId),
                            conn,
                            tx);
                    }
                    else if (req.RemoveAttribute != null)
                    {
                        var r = req.RemoveAttribute;

                        nodeId = r.NodeId;

                        newVersionId = await _attrService.RemoveAttributeAsync(
                            Guid.Parse(r.NodeId),
                            Guid.Parse(r.VersionId),
                            r.Key,
                            Guid.Parse(r.SessionId),
                            conn,
                            tx);
                    }

                    tx.Commit();

                    await responseStream.WriteAsync(new WorkGrpc.SaveNodeResponse
                    {
                        NodeId = nodeId,
                        Success = true,
                        Message = "OK",
                        VersionId = newVersionId.ToString()
                    });
                }
                catch (Exception ex)
                {
                    tx.Rollback();

                    await responseStream.WriteAsync(new WorkGrpc.SaveNodeResponse
                    {
                        NodeId = "",
                        Success = false,
                        Message = ex.Message,
                        VersionId = ""
                    });
                }
            }
        }
    }
}