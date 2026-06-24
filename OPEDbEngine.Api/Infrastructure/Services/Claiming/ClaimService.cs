using Dapper;
using OPEDbEngine.Core.Interfaces;
using OPEDbEngine.Core.Models;
using OPEDbEngine.Infrastructure.Data;
using OPEDbEngine.Infrastructure.Repositories;
using System.Data;

namespace OPEDbEngine.Infrastructure.Services.Claiming
{
    public class ClaimService : IClaimService
    {
        private readonly DbConnectionFactory _db;
        private readonly ClaimRepository _claimRepo;
        private readonly SessionRepository _sessionRepo;

        public ClaimService(DbConnectionFactory db, ClaimRepository claimRepo, SessionRepository sessionRepo)
        {
            _db = db;
            _claimRepo = claimRepo;
            _sessionRepo = sessionRepo;
        }

        // ✅ 1. Claim node (NO overwrite allowed)
        public async Task ClaimNodeAsync(
            Guid nodeId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            var exists = await _sessionRepo.SessionExists(conn, sessionId, tx);

            if (!exists)
                throw new InvalidOperationException("Session does not exist.");

            var claim = new Claim // ✅ domain object introduced
            {
                NodeId = nodeId,
                ClaimedBy = sessionId
            };

            var existing = await _claimRepo.GetOwner(conn, claim.NodeId, tx);

            if (existing != null)
                throw new InvalidOperationException("Node is already claimed.");

            await _claimRepo.InsertClaim(conn, claim.NodeId, claim.ClaimedBy);
        }

        // ✅ 2. Validate claim
        public async Task ValidateClaimAsync(
            Guid nodeId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            var exists = await _sessionRepo.SessionExists(conn, sessionId, tx);

            if (!exists)
                throw new InvalidOperationException("Session does not exist.");

            var claim = new Claim
            {
                NodeId = nodeId,
                ClaimedBy = sessionId
            };

            var owner = await _claimRepo.GetOwner(conn, claim.NodeId, tx);

            if (!owner.HasValue || owner.Value != claim.ClaimedBy)
                throw new InvalidOperationException("Node is not claimed by this session.");
        }

        // ✅ 3. Release node (ONLY owner)
        public async Task ReleaseNodeAsync(
            Guid nodeId,
            Guid sessionId,
            IDbConnection conn,
            IDbTransaction tx)
        {
            var exists = await _sessionRepo.SessionExists(conn, sessionId, tx);

            if (!exists)
                throw new InvalidOperationException("Session does not exist.");

            var claim = new Claim
            {
                NodeId = nodeId,
                ClaimedBy = sessionId
            };

            var owner = await _claimRepo.GetOwner(conn, claim.NodeId, tx);

            if (owner == null)
                throw new InvalidOperationException("Node is not claimed.");

            if (owner != claim.ClaimedBy)
                throw new InvalidOperationException("Cannot release: not owner of claim.");

            await _claimRepo.DeleteClaim(conn, claim.NodeId);
        }

        // ✅ 4. Force release (admin use)
        public async Task ForceReleaseAsync(
            Guid nodeId,
            Guid sessionId,
            string reason,
            IDbConnection conn,
            IDbTransaction tx)
        {
            var claim = new Claim
            {
                NodeId = nodeId,
                ClaimedBy = sessionId
            };

            await _claimRepo.DeleteClaim(conn, claim.NodeId, tx);
        }
    }
}
