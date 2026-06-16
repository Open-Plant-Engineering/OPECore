using Dapper;
using OPEDbEngine.Core.DTOs;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Query
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

            var node = await conn.QueryFirstOrDefaultAsync<NodeRow>(
                @"SELECT id, type, owner, current_version_id
                  FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            if (node == null)
                throw new InvalidOperationException("Node not found");

            // ✅ FINAL FIX: defensive consistency (MANDATORY in real systems)
            if (node.current_version_id == null)
            {
                // re-read once more (no loop needed)
                node = await conn.QueryFirstOrDefaultAsync<NodeRow>(
                    @"SELECT id, type, owner, current_version_id
                      FROM nodes WHERE id = @Id",
                    new { Id = nodeId });

                if (node!.current_version_id == null)
                    throw new InvalidOperationException("Node has no version");
            }

            return await BuildNode(
                conn,
                nodeId,
                node.Type,
                node.Owner,
                node.current_version_id.Value);
        }

        public async Task<NodeDto> GetNodeVersionAsync(Guid nodeId, Guid versionId)
        {
            using var conn = _db.Create();

            var node = await conn.QueryFirstOrDefaultAsync<NodeMeta>(
                @"SELECT type, owner FROM nodes WHERE id = @Id",
                new { Id = nodeId });

            if (node == null)
                throw new InvalidOperationException("Node not found");

            return await BuildNode(conn, nodeId, node.Type, node.Owner, versionId);
        }

        private async Task<NodeDto> BuildNode(
            IDbConnection conn,
            Guid nodeId,
            string type,
            string owner,
            Guid versionId)
        {
            var setId = await conn.ExecuteScalarAsync<Guid>(
                "SELECT attribute_set_id FROM versions WHERE id = @Id",
                new { Id = versionId });

            var attrs = (await conn.QueryAsync<AttributeRow>(
                @"SELECT key as Key,
                         value_hash as ValueHash,
                         value_type as ValueType
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
                var value = await ResolveValue(conn, attr.ValueHash, attr.ValueType);

                result.Attributes.Add(new AttributeDto
                {
                    Key = attr.Key,
                    ValueType = attr.ValueType,
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
            return type switch
            {
                1 => await conn.ExecuteScalarAsync<string>(
                        "SELECT value FROM string_values WHERE hash = @Hash",
                        new { Hash = hash }),

                2 => await conn.ExecuteScalarAsync<double>(
                        "SELECT value FROM number_values WHERE hash = @Hash",
                        new { Hash = hash }),

                3 => await conn.ExecuteScalarAsync<bool>(
                        "SELECT value FROM bool_values WHERE hash = @Hash",
                        new { Hash = hash }),

                _ => throw new InvalidOperationException("Unsupported type")
            };
        }

        // ✅ Internal models (no need in Core)

        private class NodeRow
        {
            public Guid Id { get; set; }
            public string Type { get; set; } = default!;
            public string Owner { get; set; } = default!;
            public Guid? current_version_id { get; set; }
        }

        private class NodeMeta
        {
            public string Type { get; set; } = default!;
            public string Owner { get; set; } = default!;
        }

        private class AttributeRow
        {
            public int Key { get; set; }
            public byte[] ValueHash { get; set; } = default!;
            public short ValueType { get; set; }
        }
    }
}