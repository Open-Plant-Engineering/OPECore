import os

class PersistentLockManager:
    def __init__(self, lock_dir="locks"):
        self.lock_dir = lock_dir
        os.makedirs(lock_dir, exist_ok=True)

    def _sanitize(self, val):
        return str(val).replace("*", "__all__")

    def _path(self, object_id, attr):
        return os.path.join(self.lock_dir, f"{object_id}_{self._sanitize(attr)}.lock")

    def acquire(self, object_id, attr, owner):
        path = self._path(object_id, attr)
        try:
            with open(path, "x") as f:
                f.write(owner)
            return True
        except FileExistsError:
            return False

    def release(self, object_id, attr, owner):
        path = self._path(object_id, attr)
        if not os.path.exists(path):
            return False
        with open(path) as f:
            if f.read() != owner:
                return False
        os.remove(path)
        return True
