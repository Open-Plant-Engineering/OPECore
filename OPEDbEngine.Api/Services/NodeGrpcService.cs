using Grpc.Core;
using OPEDbEngine.Api;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.Claiming;
using InfraNodeService = OPEDbEngine.Infrastructure.Services.Nodes.NodeService;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;

namespace OPEDbEngine.Api.Services
{
    public class NodeGrpcService : NodeService.NodeServiceBase
    {
        private readonly InfraNodeService _nodeService;
        private readonly IClaimService _claimService;
        private readonly AttributeCommandService _commandService;
        private readonly QueryService _queryService;
        private readonly IValueStoreService _valueStore;
        private readonly DbConnectionFactory _db;

        public NodeGrpcService(
            InfraNodeService nodeService,
            IClaimService claimService,
            AttributeCommandService commandService,
            QueryService queryService,
            IValueStoreService valueStore,
            DbConnectionFactory db)
        {
            _nodeService = nodeService;
            _claimService = claimService;
            _commandService = commandService;
            _queryService = queryService;
            _valueStore = valueStore;
            _db = db;
        }

        // ✅ CREATE NODE
        public override async Task<CreateNodeResponse> CreateNode(
            CreateNodeRequest request,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            var version = await _nodeService.CreateNodeAsync(
                nodeId,
                request.Type,
                request.Owner,
                sessionId,
                conn,
                tx);

            tx.Commit();

            return new CreateNodeResponse
            {
                VersionId = version.ToString()
            };
        }

        // ✅ CLAIM NODE
        public override async Task<ClaimNodeResponse> ClaimNode(
            ClaimNodeRequest request,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            await _claimService.ClaimNodeAsync(nodeId, sessionId, conn, tx);

            tx.Commit();

            return new ClaimNodeResponse
            {
                Success = true
            };
        }

        // ✅ SET ATTRIBUTE
        public override async Task<SetAttributeResponse> SetAttribute(
            SetAttributeRequest request,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.VersionId, out var versionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid versionId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            var newVersion = await _commandService.SetAttributeAsync(
                nodeId,
                versionId,
                request.Key,
                request.ValueHash.ToByteArray(),
                (short)request.ValueType,
                sessionId,
                conn,
                tx);

            tx.Commit();

            return new SetAttributeResponse
            {
                NewVersionId = newVersion.ToString()
            };
        }

        // ✅ GET NODE (READ → no TX needed)
        public override async Task<NodeResponse> GetNode(
            GetNodeRequest request,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            var node = await _queryService.GetNodeAsync(nodeId, conn);

            var response = new NodeResponse
            {
                NodeId = node.NodeId.ToString(),
                VersionId = node.VersionId.ToString(),
                Type = node.Type,
                Owner = node.Owner
            };

            foreach (var attr in node.Attributes)
            {
                response.Attributes.Add(new Attribute
                {
                    Key = attr.Key,
                    ValueType = attr.ValueType,
                    Value = attr.Value?.ToString() ?? ""
                });
            }

            return response;
        }

        // ✅ STORE VALUE (SIMPLE FLOW OK)
        public override async Task<StoreValueResponse> StoreValue(
            StoreValueRequest request,
            ServerCallContext context)
        {
            byte[] hash;
            int valueType;

            switch (request.ValueCase)
            {
                case StoreValueRequest.ValueOneofCase.StringValue:
                    hash = await _valueStore.StoreStringAsync(request.StringValue);
                    valueType = 1;
                    break;

                case StoreValueRequest.ValueOneofCase.NumberValue:
                    hash = await _valueStore.StoreNumberAsync(request.NumberValue);
                    valueType = 2;
                    break;

                case StoreValueRequest.ValueOneofCase.BoolValue:
                    hash = await _valueStore.StoreBoolAsync(request.BoolValue);
                    valueType = 3;
                    break;

                default:
                    throw new RpcException(new Status(StatusCode.InvalidArgument, "Unsupported value type"));
            }

            return new StoreValueResponse
            {
                ValueHash = Google.Protobuf.ByteString.CopyFrom(hash),
                ValueType = valueType
            };
        }

        // ✅ REMOVE ATTRIBUTE
        public override async Task<RemoveAttributeResponse> RemoveAttribute(
            RemoveAttributeRequest request,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            var nodeId = Guid.Parse(request.NodeId);
            var versionId = Guid.Parse(request.VersionId);
            var sessionId = Guid.Parse(request.SessionId);

            var newVersion = await _commandService.RemoveAttributeAsync(
                nodeId,
                versionId,
                request.Key,
                sessionId,
                conn,
                tx);

            tx.Commit();

            return new RemoveAttributeResponse
            {
                NewVersionId = newVersion.ToString()
            };
        }

        // ✅ BULK SET
        public override async Task<BulkSetAttributesResponse> BulkSetAttributes(
            BulkSetAttributesRequest request,
            ServerCallContext context)
        {
            using var conn = _db.Create();
            conn.Open();

            using var tx = conn.BeginTransaction();

            var nodeId = Guid.Parse(request.NodeId);
            var versionId = Guid.Parse(request.VersionId);
            var sessionId = Guid.Parse(request.SessionId);

            var items = request.Attributes.Select(a => new AttributeItem
            {
                Key = a.Key,
                ValueHash = a.ValueHash.ToByteArray(),
                ValueType = (short)a.ValueType
            });

            var newVersion = await _commandService.BulkSetAttributesAsync(
                nodeId,
                versionId,
                items,
                sessionId,
                conn,
                tx);

            tx.Commit();

            return new BulkSetAttributesResponse
            {
                NewVersionId = newVersion.ToString()
            };
        }
    }
}