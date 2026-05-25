from opecore.core.constants import DELETE


class AuthorizationPolicy:

    def can_update(self, object_id, obj, updates, actor, force=False):
        claim_by = obj.get("claim_by")

        # ✅ FORCE override (admin/system)
        if force:
            return True

        # ✅ Case 1: unclaimed
        if claim_by is None:
            return True

        # ✅ Case 2: claim field update
        if "claim_by" in updates:
            new_claim = updates["claim_by"]

            # ✅ delete by owner
            if new_claim is DELETE:
                return claim_by == actor

            # ✅ idempotent
            if new_claim == claim_by:
                return True

            # ❌ no transfer
            return False

        # ✅ Case 3: normal update
        return claim_by == actor
