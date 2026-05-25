import os
from typing import Optional


class PersistentLockManager:
    """
    File-based lock manager (cross-process safe).
    """

    def __init__(self, lock_dir: str = "locks"):
        self.lock_dir = lock_dir
        os.makedirs(self.lock_dir, exist_ok=True)

    # ✅ ===============================
    # INTERNAL HELPERS
    # ✅ ===============================

    def _sanitize(self, value: str) -> str:
        """
        Make attribute safe for filenames.
        """
        return str(value).replace("*", "__all__").replace(" ", "_")

    def _lock_path(self, object_id: int, attribute: str) -> str:
        safe_attr = self._sanitize(attribute)
        return os.path.join(self.lock_dir, f"{object_id}_{safe_attr}.lock")

    # ✅ ===============================
    # ACQUIRE LOCK
    # ✅ ===============================

    def acquire(self, object_id: int, attribute: str, owner: str) -> bool:
        path = self._lock_path(object_id, attribute)

        try:
            # ✅ atomic creation
            with open(path, "x") as f:
                f.write(owner)
            return True
        except FileExistsError:
            return False

    # ✅ ===============================
    # RELEASE LOCK
    # ✅ ===============================

    def release(self, object_id: int, attribute: str, owner: str) -> bool:
        path = self._lock_path(object_id, attribute)

        if not os.path.exists(path):
            return False

        try:
            with open(path, "r") as f:
                current_owner = f.read()
        except Exception:
            return False

        if current_owner != owner:
            return False

        try:
            os.remove(path)
            return True
        except FileNotFoundError:
            return False

    # ✅ ===============================
    # STATUS
    # ✅ ===============================

    def is_locked(self, object_id: int, attribute: str) -> bool:
        return os.path.exists(self._lock_path(object_id, attribute))

    def get_owner(self, object_id: int, attribute: str) -> Optional[str]:
        path = self._lock_path(object_id, attribute)

        if not os.path.exists(path):
            return None

        try:
            with open(path, "r") as f:
                return f.read()
        except Exception:
            return None