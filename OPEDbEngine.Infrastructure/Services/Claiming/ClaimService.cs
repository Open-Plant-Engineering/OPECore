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

        public async Task ClaimNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            await conn.ExecuteAsync(
                @"INSERT INTO node_claims (node_id, claimed_by)
                  VALUES (@NodeId, @Session)
                  ON CONFLICT (node_id)
                  DO UPDATE SET claimed_by = @Session",
                new
                {
                    NodeId = nodeId,
                    Session = sessionId
                });
        }

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
        
            if (!owner.HasValue || owner.Value == Guid.Empty || owner.Value != sessionId)
                throw new InvalidOperationException("Node is not claimed by this session.");
        }
    }
}