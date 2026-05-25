from opecore.core.constants import DELETE


class AuthorizationPolicy:
    def can_update(self, object_id: int, obj: dict, updates: dict, actor: str) -> bool:
        claim_by = obj.get("claim_by")

        # ✅ Case 1: unclaimed → free
        if claim_by is None:
            return True

        # ✅ Case 2: claim field is being modified
        if "claim_by" in updates:
            new_claim = updates["claim_by"]

            # ✅ allow deletion by claimer
            if new_claim is DELETE:
                return claim_by == actor

            # ✅ allow NO-CHANGE update (idempotent)
            if new_claim == claim_by:
                return True

            # ❌ block transfer
            return False

        # ✅ Case 3: normal updates → only claimer
        return claim_by == actor