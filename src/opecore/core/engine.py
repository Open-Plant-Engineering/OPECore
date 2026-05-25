from opecore.storage.engine import StorageEngine
from opecore.lock.persistent import PersistentLockManager
from opecore.index.index import IndexEngine

class Engine:
    def __init__(self, db_path="data.db"):
        self.storage = StorageEngine(db_path)
        self.lock_manager = PersistentLockManager("locks")
        self.index = IndexEngine()

    # ✅ READ
    def read_latest(self, object_id):
        return self.storage.read_latest(object_id)

    def read_as_of(self, object_id, timestamp):
        return self.storage.read_as_of(object_id, timestamp)

    # ✅ TRANSACTIONAL UPDATE
    def update_attribute(self, object_id, attribute, new_value, owner):
        # STEP 1: LOCK
        if not self.lock_manager.acquire(object_id, attribute, owner):
            raise Exception("Lock already acquired by another user")

        try:
            # STEP 2: READ CURRENT OBJECT
            current_data = self.storage.read_latest(object_id)

            if current_data is None:
                obj = {}
            else:
                obj = self._deserialize(current_data)

            # STEP 3: MODIFY
            obj[attribute] = new_value

            # STEP 4: WRITE NEW VERSION
            binary = self._serialize(obj)
            self.storage.append(object_id, binary)
            
            # ✅ update index
            self.index.add(object_id, obj)

        finally:
            # STEP 5: RELEASE LOCK
            self.lock_manager.release(object_id, attribute, owner)

    # ✅ serialization (simple for now)
    def _serialize(self, obj: dict) -> bytes:
        import json
        return json.dumps(obj).encode()

    def _deserialize(self, data: bytes) -> dict:
        import json
        return json.loads(data.decode())
