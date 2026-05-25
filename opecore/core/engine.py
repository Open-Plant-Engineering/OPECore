import json
from opecore.storage.engine import StorageEngine
from opecore.lock.persistent import PersistentLockManager
from opecore.index.index import IndexEngine

class Engine:
    def __init__(self, db_path="data.db"):
        self.storage = StorageEngine(db_path)
        self.lock = PersistentLockManager("locks")
        self.index = IndexEngine()

    def update_attribute(self, object_id, attr, value, owner):
        if not self.lock.acquire(object_id, "__all__", owner):
            raise Exception("Locked")
        try:
            data = self.storage.read_latest(object_id)
            obj = json.loads(data.decode()) if data else {}

            old_obj = obj.copy()
            obj[attr] = value

            self.storage.append(object_id, json.dumps(obj).encode())
            self.index.update(object_id, old_obj, obj)
        finally:
            self.lock.release(object_id, "__all__", owner)

    def read_latest(self, object_id):
        return self.storage.read_latest(object_id)

    def read_as_of(self, object_id, ts):
        return self.storage.read_as_of(object_id, ts)

    def query(self, k, v):
        return list(self.index.query(k, v))
