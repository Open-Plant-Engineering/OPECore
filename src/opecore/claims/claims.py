import os
import json

from opecore.storage.safe import safe_write


def is_ancestor(parent: str, child: str) -> bool:
    return child.startswith(parent + "/")


class ClaimManager:
    def __init__(self, db_path: str):
        self.file = os.path.join(db_path, "claims.json")

        if not os.path.exists(self.file):
            safe_write(self.file, b"[]")

    def load(self):
        with open(self.file, "r") as f:
            return json.load(f)

    def save(self, claims):
        data = json.dumps(claims).encode()
        safe_write(self.file, data)

    # 🔥 CORE LOGIC
    def can_claim(self, target, claim_type, claims, user):
        for c in claims:
            path = c["path"]
            ctype = c["type"]
            owner = c["owner"]

            if owner == user:
                continue

            # ✅ Rule 1: Same node conflict
            if path == target:
                return False

            # ✅ Rule 4: prevent subtree escalation
            if claim_type == "SUBTREE":
                if is_ancestor(target, path):
                    return False

            # ✅ Rule 2: subtree blocks descendants
            if ctype == "SUBTREE":
                if is_ancestor(path, target):
                    return False

        return True

    def claim(self, user, path, claim_type):
        claims = self.load()

        if not self.can_claim(path, claim_type, claims, user):
            return False

        claims.append({
            "path": path,
            "type": claim_type,
            "owner": user
        })

        self.save(claims)
        return True

    def release(self, user, path):
        claims = self.load()

        claims = [
            c for c in claims
            if not (c["owner"] == user and c["path"] == path)
        ]

        self.save(claims)