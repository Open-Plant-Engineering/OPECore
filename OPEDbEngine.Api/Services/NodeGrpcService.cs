using Grpc.Core;
using OPEDbEngine.Api;
using OPEDbEngine.Core.Interfaces;

namespace OPEDbEngine.Api.Services
{
    public class NodeGrpcService : NodeService.NodeServiceBase
    {
        private readonly IQueryService _query;

        public NodeGrpcService(IQueryService query)
        {
            _query = query;
        }

        public override async Task<NodeResponse> GetNode(
            GetNodeRequest request,
            ServerCallContext context)
        {
            var nodeId = Guid.Parse(request.NodeId);

            var node = await _query.GetNodeAsync(nodeId);

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
    }
}