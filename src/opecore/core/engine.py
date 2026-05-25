from typing import Optional, List
import json

from opecore.storage.engine import StorageEngine
from opecore.lock.persistent import PersistentLockManager
from opecore.index.index import IndexEngine
from opecore.core.constants import DELETE
from opecore.transaction.transaction import Transaction
from opecore.auth.policy import AuthorizationPolicy


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
        self.auth = AuthorizationPolicy()
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

    def query_advanced(self, filters: dict):
        result = set()

        for object_id in self.index.get_all_objects():
            data = self._deserialize(self.storage.read_latest(object_id))

            match = True

            for key, value in filters.items():
                if key.startswith("__"):
                    continue
                
                if data.get(key) != value:
                    match = False
                    break

            if match:
                result.add(object_id)

        return result

    def query_or(self, conditions: list):
        """
        conditions = [
            {"type": "Device"},
            {"type": "Site"}
        ]
        """

        result = set()

        for cond in conditions:
            partial = self.query_multiple(cond)
            result = result.union(partial)

        return result

    def query_multiple(self, filters: dict):
        """
        filters = {
            "type": "Device",
            "owner": 1
        }
        """

        if not filters:
            return set()

        result_sets = []

        for key, value in filters.items():
            ids = set(self.query(key, value))
            result_sets.append(ids)

        # ✅ intersection (AND logic)
        result = result_sets[0]

        for s in result_sets[1:]:
            result = result.intersection(s)

        return result
    
    def query_complex(self, query: dict):
        """
        Example:
        {
            "AND": {"owner": 1},
            "OR": [
                {"type": "Device"},
                {"type": "Site"}
            ]
        }
        """

        result = None

        # ✅ AND part
        if "AND" in query:
            result = self.query_multiple(query["AND"])

        # ✅ OR part
        if "OR" in query:
            or_result = self.query_or(query["OR"])

            if result is None:
                result = or_result
            else:
                result = result.intersection(or_result)

        return result if result else set()

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

    def update_object(self, object_id: int, updates: dict, actor: str, force: bool = False):
        lock_key = "__all__"

        if not force:
            if not self.lock_manager.acquire(object_id, lock_key, actor):
                raise Exception(f"Object {object_id} is locked")
        else:
            # ✅ force override → skip lock check
            pass
        
        try:
            # ✅ MUST USE prepare
            new_obj, old_obj = self._prepare_object(object_id, updates, actor, force)

            binary = self._serialize(new_obj)
            self.storage.append(object_id, binary)

            self._update_index(object_id, old_obj, new_obj)

        finally:
            self.lock_manager.release(object_id, lock_key, actor)

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

    def _prepare_object(self, object_id, updates, actor=None, force=False):
        current_data = self.storage.read_latest(object_id)

        if current_data is None:
            obj = {}
        else:
            obj = self._deserialize(current_data)

        # ✅ AUTH CHECK
        if actor is not None:
            if not self.auth.can_update(object_id, obj, updates, actor, force):
                raise Exception(f"Unauthorized update on object {object_id}")

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

    def _get_object_version(self, object_id):
        data = self.storage.read_latest(object_id)
    
        if data is None:
            return None
    
        # ✅ version = raw content snapshot (simple + safe)
        return data
    
    def get_parent(self, object_id):
        data = self.storage.read_latest(object_id)
    
        if not data:
            return None
    
        obj = self._deserialize(data)
        return obj.get("owner")
    
    def get_children(self, parent_id):
        return list(self.query("owner", parent_id))
    
    def get_ancestors(self, object_id):
        ancestors = []
        current = object_id
    
        while True:
            parent = self.get_parent(current)
    
            if parent is None:
                break
            
            ancestors.append(parent)
            current = parent
    
        return ancestors
    
    def get_subtree(self, root_id):
        result = set()
        stack = [root_id]
    
        while stack:
            current = stack.pop()
            result.add(current)
    
            children = self.get_children(current)
            stack.extend(children)
    
        return result
    
