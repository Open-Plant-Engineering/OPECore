using Dapper;
using OPEDbEngine.Infrastructure.Data;

namespace OPEDbEngine.Infrastructure.Service.Claiming
{
    public class ClaimService : IClaimService
    {
        private readonly DbConnectionFactory _db;
    
        public ClaimService(DbConnectionFactory db)
        {
            _db = db;
        }
    
        public async Task ClaimNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();
    
            using var tx = conn.BeginTransaction();
    
            // Check existing claim
            var existing = await conn.QueryFirstOrDefaultAsync<Guid?>(
                "SELECT claimed_by FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId },
                tx);
    
            if (existing.HasValue)
            {
                if (existing.Value == sessionId)
                {
                    tx.Commit(); // already claimed by same session
                    return;
                }
    
                throw new InvalidOperationException("Node already claimed by another session.");
            }
    
            // Insert claim
            await conn.ExecuteAsync(
                @"INSERT INTO node_claims (node_id, claimed_by)
              VALUES (@NodeId, @SessionId)",
                new { NodeId = nodeId, SessionId = sessionId },
                tx);
    
            // Audit log
            await conn.ExecuteAsync(
                @"INSERT INTO claim_audit_log 
              (id, node_id, action, performed_by)
              VALUES (@Id, @NodeId, 'CLAIM', @Session)",
                new
                {
                    Id = Guid.NewGuid(),
                    NodeId = nodeId,
                    Session = sessionId
                },
                tx);
    
            tx.Commit();
        }
    
        public async Task ReleaseNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();
    
            using var tx = conn.BeginTransaction();
    
            var existing = await conn.QueryFirstOrDefaultAsync<Guid?>(
                "SELECT claimed_by FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId },
                tx);
    
            if (!existing.HasValue)
                throw new InvalidOperationException("Node is not claimed.");
    
            if (existing.Value != sessionId)
                throw new InvalidOperationException("Cannot release claim owned by another session.");
    
            // Delete claim
            await conn.ExecuteAsync(
                "DELETE FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId },
                tx);
    
            // Audit log
            await conn.ExecuteAsync(
                @"INSERT INTO claim_audit_log
              (id, node_id, action, performed_by)
              VALUES (@Id, @NodeId, 'RELEASE', @Session)",
                new
                {
                    Id = Guid.NewGuid(),
                    NodeId = nodeId,
                    Session = sessionId
                },
                tx);
    
            tx.Commit();
        }
    
        public async Task ForceReleaseAsync(Guid nodeId, Guid sessionId, string reason)
        {
            using var conn = _db.Create();
            conn.Open();
    
            using var tx = conn.BeginTransaction();
    
            var existing = await conn.QueryFirstOrDefaultAsync<Guid?>(
                "SELECT claimed_by FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId },
                tx);
    
            if (!existing.HasValue)
            {
                tx.Commit();
                return; // already free
            }
    
            await conn.ExecuteAsync(
                "DELETE FROM node_claims WHERE node_id = @NodeId",
                new { NodeId = nodeId },
                tx);
    
            await conn.ExecuteAsync(
                @"INSERT INTO claim_audit_log
              (id, node_id, action, performed_by, reason)
              VALUES (@Id, @NodeId, 'FORCE_RELEASE', @Session, @Reason)",
                new
                {
                    Id = Guid.NewGuid(),
                    NodeId = nodeId,
                    Session = sessionId,
                    Reason = reason
                },
                tx);
    
            tx.Commit();
        }
    }
}
