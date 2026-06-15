using Dapper;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Service.Query.Models;
using System.Data;

namespace OPEDbEngine.Infrastructure.Service.Query
{
    public class QueryService : IQueryService
    {
        private readonly DbConnectionFactory _db;

        public QueryService(DbConnectionFactory db)
        {
            _db = db;
        }

        public async Task<NodeDto> GetNodeAsync(Guid nodeId)
        {
            using var conn = _db.Create();

            var row = await conn.QueryFirstOrDefaultAsync(
                @"SELECT id, type, owner, current_version_id
                  FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            if (row == null)
                throw new InvalidOperationException("Node not found");

            return await BuildNodeDto(conn, row.id, row.type, row.owner, row.current_version_id);
        }

        public async Task<NodeDto> GetNodeVersionAsync(Guid nodeId, Guid versionId)
        {
            using var conn = _db.Create();

            var node = await conn.QueryFirstOrDefaultAsync(
                "SELECT type, owner FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            if (node == null)
                throw new InvalidOperationException("Node not found");

            return await BuildNodeDto(conn, nodeId, node.type, node.owner, versionId);
        }

        private async Task<NodeDto> BuildNodeDto(
            IDbConnection conn,
            Guid nodeId,
            string type,
            string owner,
            Guid versionId)
        {
            // ✅ Get attribute set
            var setId = await conn.ExecuteScalarAsync<Guid>(
                "SELECT attribute_set_id FROM versions WHERE id = @Id",
                new { Id = versionId });

            // ✅ Get attributes
            var attrs = (await conn.QueryAsync(
                @"SELECT key, value_hash, value_type
                  FROM attribute_set_items
                  WHERE set_id = @SetId",
                new { SetId = setId })).ToList();

            var result = new NodeDto
            {
                NodeId = nodeId,
                VersionId = versionId,
                Type = type,
                Owner = owner
            };

            foreach (var attr in attrs)
            {
                var value = await ResolveValue(conn, attr.value_hash, attr.value_type);

                result.Attributes.Add(new AttributeDto
                {
                    Key = attr.key,
                    ValueType = attr.value_type,
                    Value = value
                });
            }

            return result;
        }

        private async Task<object?> ResolveValue(
            IDbConnection conn,
            byte[] hash,
            short type)
        {
            switch (type)
            {
                case 1: // string
                    return await conn.ExecuteScalarAsync<string>(
                        "SELECT value FROM string_values WHERE hash = @Hash",
                        new { Hash = hash });

                case 2: // number
                    return await conn.ExecuteScalarAsync<double>(
                        "SELECT value FROM number_values WHERE hash = @Hash",
                        new { Hash = hash });

                case 3: // bool
                    return await conn.ExecuteScalarAsync<bool>(
                        "SELECT value FROM bool_values WHERE hash = @Hash",
                        new { Hash = hash });

                case 4: // list
                    return await conn.ExecuteScalarAsync<byte[]>(
                        "SELECT value FROM list_values WHERE hash = @Hash",
                        new { Hash = hash });

                default:
                    throw new InvalidOperationException("Unsupported type");
            }
        }
    }
}
