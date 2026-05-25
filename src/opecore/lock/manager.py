import time


class LockManager:
    def __init__(self):
        self.locks = {}   # (object_id, attribute) → owner

    def acquire(self, object_id, attribute, owner):
        key = (object_id, attribute)

        if key in self.locks:
            return False  # already locked

        self.locks[key] = {
            "owner": owner,
            "timestamp": time.time()
        }
        return True

    def release(self, object_id, attribute, owner):
        key = (object_id, attribute)

        if key not in self.locks:
            return False

        if self.locks[key]["owner"] != owner:
            return False  # not owner

        del self.locks[key]
        return True

    def is_locked(self, object_id, attribute):
        return (object_id, attribute) in self.locks

    def get_owner(self, object_id, attribute):
        key = (object_id, attribute)
        return self.locks.get(key)