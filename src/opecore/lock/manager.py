import time
from typing import Dict, Tuple, Optional


class LockManager:
    """
    In-memory lock manager (single-process use).
    """

    def __init__(self):
        # (object_id, attribute) -> { owner, timestamp }
        self.locks: Dict[Tuple[int, str], dict] = {}

    # ✅ ===============================
    # ACQUIRE LOCK
    # ✅ ===============================

    def acquire(self, object_id: int, attribute: str, owner: str) -> bool:
        key = (object_id, attribute)

        if key in self.locks:
            return False

        self.locks[key] = {
            "owner": owner,
            "timestamp": time.time(),
        }

        return True

    # ✅ ===============================
    # RELEASE LOCK
    # ✅ ===============================

    def release(self, object_id: int, attribute: str, owner: str) -> bool:
        key = (object_id, attribute)

        lock = self.locks.get(key)
        if not lock:
            return False

        if lock["owner"] != owner:
            return False

        del self.locks[key]
        return True

    # ✅ ===============================
    # STATUS
    # ✅ ===============================

    def is_locked(self, object_id: int, attribute: str) -> bool:
        return (object_id, attribute) in self.locks

    def get_owner(self, object_id: int, attribute: str) -> Optional[str]:
        lock = self.locks.get((object_id, attribute))
        if not lock:
            return None
        return lock["owner"]
