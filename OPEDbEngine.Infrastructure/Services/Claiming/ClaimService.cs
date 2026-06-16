using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Claiming
{
    public class ClaimService : IClaimService
    {
        private readonly DbConnectionFactory _db;

        public ClaimService(DbConnectionFactory db)
        {
            _db = db;
        }

        // ✅ 1. Claim node (NO overwrite allowed)
        public async Task ClaimNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            var existing = await conn.ExecuteScalarAsync<Guid?>(
                "SELECT claimed_by FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId });

            if (existing != null)
                throw new InvalidOperationException("Node is already claimed.");

            await conn.ExecuteAsync(
                @"INSERT INTO node_claims (node_id, claimed_by)
                  VALUES (@NodeId, @Session)",
                new
                {
                    NodeId = nodeId,
                    Session = sessionId
                });
        }

        // ✅ 2. Validate claim
        public async Task ValidateClaimAsync(
            Guid nodeId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            var owner = await conn.QueryFirstOrDefaultAsync<Guid?>(
                @"SELECT claimed_by 
                  FROM node_claims 
                  WHERE node_id = @NodeId",
                new { NodeId = nodeId },
                tx);

            if (!owner.HasValue || owner.Value != sessionId)
                throw new InvalidOperationException("Node is not claimed by this session.");
        }

        // ✅ 3. Release node (ONLY owner)
        public async Task ReleaseNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            var owner = await conn.ExecuteScalarAsync<Guid?>(
                "SELECT claimed_by FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId });

            if (!owner.HasValue)
                throw new InvalidOperationException("Node is not claimed.");

            if (owner.Value != sessionId)
                throw new InvalidOperationException("Cannot release: not owner of claim.");

            await conn.ExecuteAsync(
                "DELETE FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId });
        }

        // ✅ 4. Force release (admin use)
        public async Task ForceReleaseAsync(Guid nodeId, Guid sessionId, string reason)
        {
            using var conn = _db.Create();
            conn.Open();

            // optional: log reason later

            await conn.ExecuteAsync(
                "DELETE FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId });
        }
    }
}
