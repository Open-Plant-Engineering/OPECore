from opecore.models.exceptions import ClaimError

class ClaimService:

    @staticmethod
    def claim(conn, node_id, user):
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO claims(node_id, claimed_by, claimed_at)
            VALUES (%s, %s, now())
            ON CONFLICT (node_id) DO NOTHING
            """, (node_id, user))

    @staticmethod
    def release(conn, node_id, user):
        with conn.cursor() as cur:
            cur.execute("""
            DELETE FROM claims
            WHERE node_id=%s AND claimed_by=%s
            """, (node_id, user))

    @staticmethod
    def validate(conn, node_id, user):
        with conn.cursor() as cur:
            cur.execute("""
            SELECT 1 FROM claims
            WHERE node_id=%s AND claimed_by=%s
            """, (node_id, user))

            if cur.fetchone() is None:
                raise ClaimError("Node not claimed by user")
