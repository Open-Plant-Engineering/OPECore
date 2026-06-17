namespace OPEDbEngine.Infrastructure.Sql;

public static class ClaimSql
{
    public const string GetClaimOwner = @"
        SELECT claimed_by 
        FROM node_claims 
        WHERE node_id = @NodeId";

    public const string InsertClaim = @"
        INSERT INTO node_claims (node_id, claimed_by)
        VALUES (@NodeId, @Session)";

    public const string DeleteClaim = @"
        DELETE FROM node_claims 
        WHERE node_id = @NodeId";
}
