from typing import Optional, List
import json

from opecore.storage.engine import StorageEngine
from opecore.lock.persistent import PersistentLockManager
from opecore.index.index import IndexEngine
from opecore.core.constants import DELETE
from opecore.transaction.transaction import Transaction


class Engine:
    """
    High-level orchestration layer.

    Responsibilities:
    - coordinate locking
    - manage object updates
    - integrate storage + index
    """

    def __init__(self, db_path: str = "data.db"):
        self.storage = StorageEngine(db_path)
        self.lock_manager = PersistentLockManager("locks")
        self.index = IndexEngine()
        self._rebuild_index()

    # ✅ ===============================
    # READ OPERATIONS
    # ✅ ===============================

    def read_latest(self, object_id: int) -> Optional[bytes]:
        return self.storage.read_latest(object_id)

    def read_as_of(self, object_id: int, timestamp: float) -> Optional[bytes]:
        return self.storage.read_as_of(object_id, timestamp)

    def query(self, key: str, value) -> List[int]:
        return list(self.index.query(key, value))

    # ✅ ===============================
    # WRITE OPERATIONS
    # ✅ ===============================

    def update_attribute(
        self,
        object_id: int,
        attribute: str,
        new_value,
        owner: str,
    ):
        """
        Wrapper over update_object (single field).
        """
        self.update_object(object_id, {attribute: new_value}, owner)
    

    # ✅ ===============================
    # INTERNAL HELPERS
    # ✅ ===============================

    def _update_index(self, object_id: int, old_obj: dict, new_obj: dict):
        self.index.update(object_id, old_obj, new_obj)

    def _serialize(self, obj: dict) -> bytes:
        return json.dumps(obj, separators=(",", ":")).encode()

    def _deserialize(self, data: bytes) -> dict:
        return json.loads(data.decode())

    def _rebuild_index(self):
        """
        Build index from storage on startup.
        """
    
        all_data = self.storage.read_all_latest()
    
        for object_id, data in all_data.items():
            obj = self._deserialize(data)
    
            # no old state → everything is new
            self.index.update(object_id, {}, obj)

    def update_object(
        self,
        object_id: int,
        updates: dict,
        owner: str,
    ):
        """
        Multi-field atomic update (transaction).
        """

        lock_key = "__all__"

        # ✅ STEP 1: lock
        if not self.lock_manager.acquire(object_id, lock_key, owner):
            raise Exception(f"Object {object_id} is locked")

        try:
            # ✅ STEP 2: read current
            current_data = self.storage.read_latest(object_id)

            if current_data is None:
                obj = {}
            else:
                obj = self._deserialize(current_data)
    
            old_obj = obj.copy()
    
            # ✅ APPLY ALL CHANGES SAFELY
            for key, value in updates.items():
                if value is DELETE:
                    obj.pop(key, None)
                else:
                    obj[key] = value
    
            # ✅ SERIALIZE BEFORE WRITING
            binary = self._serialize(obj)
    
            # ✅ ONLY NOW WRITE (safe point)
            self.storage.append(object_id, binary)
    
            # ✅ UPDATE INDEX AFTER SUCCESS
            self._update_index(object_id, old_obj, obj)
    
        except Exception as e:
            # ✅ NOTHING WRITTEN → safe rollback (implicit)
            raise e
    
        finally:
            # ✅ release lock
            self.lock_manager.release(object_id, lock_key, owner)

    def begin_transaction(self, owner: str):
        return Transaction(self, owner)

    def _apply_transaction_update(self, object_id: int, updates: dict):
        """
        INTERNAL: used by transaction commit.
        """

        current_data = self.storage.read_latest(object_id)

        if current_data is None:
            obj = {}
        else:
            obj = self._deserialize(current_data)

        old_obj = obj.copy()

        for key, value in updates.items():
            if value is DELETE:
                obj.pop(key, None)
            else:
                obj[key] = value

        binary = self._serialize(obj)
        self.storage.append(object_id, binary)

        self._update_index(object_id, old_obj, obj)

    def _prepare_object(self, object_id, updates):
        current_data = self.storage.read_latest(object_id)

        if current_data is None:
            obj = {}
        else:
            obj = self._deserialize(current_data)

        old_obj = obj.copy()

        for key, value in updates.items():
            if value is DELETE:
                obj.pop(key, None)
            else:
                obj[key] = value

        return obj, old_obj

    def _commit_object(self, object_id, old_obj, new_obj):
        binary = self._serialize(new_obj)
        self.storage.append(object_id, binary)
    
        self._update_index(object_id, old_obj, new_obj)
