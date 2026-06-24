using Grpc.Core;
using WorkGrpc = OPEDbEngine.gRPC.Work;
using NodeGrpc = OPEDbEngine.gRPC.Node;

using OPEDbEngine.Core.Models;       // for AttributeItem
using OPEDbEngine.Infrastructure.Mappers;

using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using DomainVersion = OPEDbEngine.Core.Models.Version;


namespace OPEDbEngine.Api.Services
{
    public class WorkGrpcService : WorkGrpc.WorkService.WorkServiceBase
    {
        private readonly INodeService _nodeService;
        private readonly IAttributeCommandService _attrService;
        private readonly DbConnectionFactory _db;
        private readonly IQueryService _queryService;
        private readonly VersionRepository _versionRepo;
        private readonly AttributeRepository _attributeRepo;

        public WorkGrpcService(
            INodeService nodeService,
            IAttributeCommandService attrService,
            IQueryService queryService,
            VersionRepository versionRepo,
            AttributeRepository attributeRepo,
            DbConnectionFactory db)
        {
            _nodeService = nodeService;
            _attrService = attrService;
            _queryService = queryService;
            _versionRepo = versionRepo;
            _attributeRepo = attributeRepo;
            _db = db;
        }

        public override async Task StreamSaveChanges(
            IAsyncStreamReader<WorkGrpc.SaveNodeRequest> requestStream,
            IServerStreamWriter<WorkGrpc.SaveNodeResponse> responseStream,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            await foreach (var req in requestStream.ReadAllAsync(context.CancellationToken))
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

            conn.Close();
            conn.Dispose();
        }

        public override async Task StreamGetWork(
            WorkGrpc.GetWorkRequest request,
            IServerStreamWriter<WorkGrpc.GetWorkResponse> responseStream,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();
            
            try
            {
                var node = await _queryService.GetNodeAsync(
                    Guid.Parse(request.NodeId),
                    conn,
                    null);

                // ✅ Map to gRPC response
                var response = new WorkGrpc.GetWorkResponse
                {
                    NodeId = node.NodeId.ToString(),
                    VersionId = node.VersionId.ToString()
                };

                foreach (var attr in node.Attributes)
                {
                    response.Attributes.Add(new WorkGrpc.AttributeSnapshot
                    {
                        Key = attr.Key,
                        ValueType = attr.ValueType,
                        Value = attr.Value?.ToString() ?? ""
                    });
                }

                // ✅ Stream (single message for now)
                await responseStream.WriteAsync(response);
            }
            catch (Exception)
            {
                // ✅ Always return structured failure instead of crashing stream
                await responseStream.WriteAsync(new WorkGrpc.GetWorkResponse
                {
                    NodeId = request.NodeId,
                    VersionId = "",
                });
            }

            conn.Close();
            conn.Dispose();
        }

        public override async Task StreamNodeHistory(
            WorkGrpc.NodeHistoryRequest request,
            IServerStreamWriter<WorkGrpc.NodeHistoryResponse> responseStream,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            try
            {
                var nodeId = Guid.Parse(request.NodeId);

                // ✅ get all versions
                IEnumerable<DomainVersion> versions = (IEnumerable<Core.Models.Version>)await _versionRepo.GetVersionsByNode(conn, nodeId);

                Dictionary<int, AttributeItem>? prev = null;

                foreach (var v in versions)
                {
                    var rows = await _attributeRepo.GetBySetId(conn, v.AttributeSetId, null);

                    var current = rows
                        .Select(r => AttributeMapper.ToDomain(r))
                        .ToDictionary(x => x.Key);

                    var changes = new List<WorkGrpc.AttributeSnapshot>();

                    if (prev == null)
                    {
                        // ✅ first version → all attributes
                        foreach (var item in current.Values)
                        {
                            changes.Add(new WorkGrpc.AttributeSnapshot
                            {
                                Key = item.Key,
                                ValueType = item.ValueType,
                                Value = ""
                            });
                        }
                    }
                    else
                    {
                        // ✅ added or updated
                        foreach (var kvp in current)
                        {
                            var key = kvp.Key;
                            var val = kvp.Value;

                            if (!prev.TryGetValue(key, out var oldVal) ||
                                !oldVal.ValueHash.SequenceEqual(val.ValueHash))
                            {
                                changes.Add(new WorkGrpc.AttributeSnapshot
                                {
                                    Key = key,
                                    ValueType = val.ValueType,
                                    Value = ""
                                });
                            }
                        }

                        // ✅ removed
                        foreach (var key in prev.Keys)
                        {
                            if (!current.ContainsKey(key))
                            {
                                changes.Add(new WorkGrpc.AttributeSnapshot
                                {
                                    Key = key,
                                    ValueType = 0,
                                    Value = "[REMOVED]"
                                });
                            }
                        }
                    }

                    await responseStream.WriteAsync(new WorkGrpc.NodeHistoryResponse
                    {
                        NodeId = request.NodeId,
                        VersionId = v.Id.ToString(),
                        ParentVersionId = v.ParentVersionId?.ToString() ?? "",
                        // ✅ TEMP: no session / timestamp in current model
                        SessionId = "",
                        Timestamp = 0,
                        Attributes = { changes }
                    });

                    prev = current;
                }
            }
            catch
            {
                await responseStream.WriteAsync(new WorkGrpc.NodeHistoryResponse
                {
                    NodeId = request.NodeId
                });
            }

            conn.Close();
            conn.Dispose();
        }

    }
}