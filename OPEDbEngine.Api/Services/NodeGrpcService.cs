using Grpc.Core;
using OPEDbEngine.Api;
using OPEDbEngine.Infrastructure.Services.Nodes;
using OPEDbEngine.Infrastructure.Services.Attributes;
using OPEDbEngine.Infrastructure.Services.Query;
using OPEDbEngine.Infrastructure.Services.Claiming;
using InfraNodeService = OPEDbEngine.Infrastructure.Services.Nodes.NodeService;
using OPEDbEngine.Infrastructure.Services.ValueStore;
using OPEDbEngine.Infrastructure.Services.Hashing;
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

        public NodeGrpcService(
            InfraNodeService nodeService,
            IClaimService claimService,
            AttributeCommandService commandService,
            QueryService queryService,
            IValueStoreService valueStore )
        {
            _nodeService = nodeService;
            _claimService = claimService;
            _commandService = commandService;
            _queryService = queryService;
            _valueStore = valueStore;
        }

        // ✅ CREATE NODE
        public override async Task<CreateNodeResponse> CreateNode(
            CreateNodeRequest request,
            ServerCallContext context)
        {
            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            var version = await _nodeService.CreateNodeAsync(
                nodeId,
                request.Type,
                request.Owner,
                sessionId);

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
            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            await _claimService.ClaimNodeAsync(nodeId, sessionId);

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
            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.VersionId, out var versionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid versionId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            if (request.ValueHash == null || request.ValueHash.Length == 0)
                throw new RpcException(new Status(StatusCode.InvalidArgument, "valueHash is required"));

            var newVersion = await _commandService.SetAttributeAsync(
                nodeId,
                versionId,
                request.Key,
                request.ValueHash.ToByteArray(),
                (short)request.ValueType,
                sessionId);

            return new SetAttributeResponse
            {
                NewVersionId = newVersion.ToString()
            };
        }

        // ✅ GET NODE
        public override async Task<NodeResponse> GetNode(
            GetNodeRequest request,
            ServerCallContext context)
        {
            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            var node = await _queryService.GetNodeAsync(nodeId);

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

        public override async Task<StoreValueResponse> StoreValue(
            StoreValueRequest request,
            ServerCallContext context)
        {
            if (request.ValueCase == StoreValueRequest.ValueOneofCase.None)
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Value is required"));

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
        
        public override async Task<RemoveAttributeResponse> RemoveAttribute(
            RemoveAttributeRequest request,
            ServerCallContext context)
        {
            if (!Guid.TryParse(request.NodeId, out var nodeId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid nodeId"));

            if (!Guid.TryParse(request.VersionId, out var versionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid versionId"));

            if (!Guid.TryParse(request.SessionId, out var sessionId))
                throw new RpcException(new Status(StatusCode.InvalidArgument, "Invalid sessionId"));

            try
            {
                var newVersion = await _commandService.RemoveAttributeAsync(
                    nodeId,
                    versionId,
                    request.Key,
                    sessionId);

                return new RemoveAttributeResponse
                {
                    NewVersionId = newVersion.ToString()
                };
            }
            catch (InvalidOperationException ex)
            {
                throw new RpcException(new Status(StatusCode.FailedPrecondition, ex.Message));
            }
            catch (Exception ex)
            {
                throw new RpcException(new Status(StatusCode.Internal, ex.Message));
            }
        }

        public override async Task<BulkSetAttributesResponse> BulkSetAttributes(
            BulkSetAttributesRequest request,
            ServerCallContext context)
        {
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
                sessionId);

            return new BulkSetAttributesResponse
            {
                NewVersionId = newVersion.ToString()
            };
        }

        public override async Task<BulkRemoveAttributesResponse> BulkRemoveAttributes(
            BulkRemoveAttributesRequest request,
            ServerCallContext context)
        {
            var nodeId = Guid.Parse(request.NodeId);
            var versionId = Guid.Parse(request.VersionId);
            var sessionId = Guid.Parse(request.SessionId);

            // ✅ call single remove logic but multiple keys
            var newVersion = await _commandService.RemoveAttributesAsync(
                nodeId,
                versionId,
                request.Keys,
                sessionId);

            return new BulkRemoveAttributesResponse
            {
                NewVersionId = newVersion.ToString()
            };
        }

    }
}