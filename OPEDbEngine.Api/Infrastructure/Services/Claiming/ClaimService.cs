using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Claiming
{
    public class ClaimService : IClaimService
    {
        private readonly DbConnectionFactory _db;
        private readonly ClaimRepository _claimRepo;

        public ClaimService(DbConnectionFactory db, ClaimRepository claimRepo)
        {
            _db = db;
            _claimRepo = claimRepo;
        }

        // ✅ 1. Claim node (NO overwrite allowed)
        public async Task ClaimNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            var existing = await _claimRepo.GetOwner(conn, nodeId);

            if (existing != null)
                throw new InvalidOperationException("Node is already claimed.");

            await _claimRepo.InsertClaim(conn, nodeId, sessionId);
        }

        // ✅ 2. Validate claim
        public async Task ValidateClaimAsync(
            Guid nodeId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            var owner = await _claimRepo.GetOwner(conn, nodeId, tx);

            if (!owner.HasValue || owner.Value != sessionId)
                throw new InvalidOperationException("Node is not claimed by this session.");

        }

        // ✅ 3. Release node (ONLY owner)
        public async Task ReleaseNodeAsync(Guid nodeId, Guid sessionId)
        {
            using var conn = _db.Create();
            conn.Open();

            var owner = await _claimRepo.GetOwner(conn, nodeId);

            if (!owner.HasValue)
                throw new InvalidOperationException("Node is not claimed.");

            if (owner.Value != sessionId)
                throw new InvalidOperationException("Cannot release: not owner of claim.");

            await _claimRepo.DeleteClaim(conn, nodeId);
        }

        // ✅ 4. Force release (admin use)
        public async Task ForceReleaseAsync(Guid nodeId, Guid sessionId, string reason)
        {
            using var conn = _db.Create();
            conn.Open();
            
            await _claimRepo.DeleteClaim(conn, nodeId);
        }
    }
}
