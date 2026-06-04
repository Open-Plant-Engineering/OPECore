from opecore.models.exceptions import ClaimError

class ClaimService:

    @staticmethod
    def claim(conn, node_id, user):

        with conn.cursor() as cur:

            # ✅ check existing claim
            cur.execute("""
            SELECT claimed_by FROM claims WHERE node_id=%s
            """, (node_id,))

            row = cur.fetchone()

            if row:
                existing_user = row["claimed_by"]

                # ✅ same user → idempotent
                if existing_user == user:
                    return

                # ❌ different user → conflict
                raise ClaimError(
                    f"Node already claimed by {existing_user}"
                )

            # ✅ no claim → insert
            cur.execute("""
            INSERT INTO claims(node_id, claimed_by, claimed_at)
            VALUES (%s, %s, now())
            """, (node_id, user))

        conn.commit()

    @staticmethod
    def release(conn, node_id, user):
        with conn.cursor() as cur:
            cur.execute("""
            DELETE FROM claims
            WHERE node_id=%s AND claimed_by=%s
            """, (node_id, user))
        conn.commit()

    @staticmethod
    def validate(conn, node_id, user):
    
        with conn.cursor() as cur:
            cur.execute("""
            SELECT claimed_by FROM claims WHERE node_id=%s
            """, (node_id,))
    
            row = cur.fetchone()
    
            if not row:
                raise ClaimError("Node is not claimed")
    
            if row["claimed_by"] != user:
                raise ClaimError("Node claimed by another user")
    