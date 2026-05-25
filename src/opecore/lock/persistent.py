import os


class PersistentLockManager:
    def __init__(self, lock_dir="locks"):
        self.lock_dir = lock_dir
        os.makedirs(lock_dir, exist_ok=True)

    def _lock_path(self, object_id, attribute):
        return os.path.join(self.lock_dir, f"{object_id}_{attribute}.lock")

    def acquire(self, object_id, attribute, owner):
        path = self._lock_path(object_id, attribute)

        if os.path.exists(path):
            return False

        try:
            with open(path, "x") as f:   # atomic create
                f.write(owner)
            return True
        except FileExistsError:
            return False

    def release(self, object_id, attribute, owner):
        path = self._lock_path(object_id, attribute)

        if not os.path.exists(path):
            return False

        with open(path, "r") as f:
            current_owner = f.read()

        if current_owner != owner:
            return False

        os.remove(path)
        return True

    def is_locked(self, object_id, attribute):
        return os.path.exists(self._lock_path(object_id, attribute))