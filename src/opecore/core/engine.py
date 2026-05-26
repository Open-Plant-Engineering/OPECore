from typing import Optional, List
import json
import os
import time
import uuid
from opecore.storage.engine import StorageEngine
from opecore.lock.persistent import PersistentLockManager
from opecore.index.index import IndexEngine
from opecore.core.constants import DELETE
from opecore.transaction.transaction import Transaction
from opecore.auth.policy import AuthorizationPolicy
from opecore.core.file_lock import FileLock   # ✅ NEW


class Engine:
    def __init__(self, db_path: str = "data.db"):
        self.storage = StorageEngine(db_path)

        # ✅ object-level locks
        self.lock_manager = PersistentLockManager("locks")

        # ✅ global writer lock (CRITICAL for WAL)
        self.file_lock = FileLock(db_path + ".lock")

        self.index = IndexEngine()
        self.auth = AuthorizationPolicy()
        self.active_transactions = {}
        self.latest_seen_version = {}

        self.node_id = self._load_or_create_node_id(db_path)
        
        self._rebuild_index()

    # ✅ ===============================
    # READ
    # ✅ ===============================

    def read_latest(self, object_id: int) -> Optional[bytes]:
        return self.storage.read_latest(object_id)

    def read_as_of(self, object_id: int, timestamp: float) -> Optional[bytes]:
        return self.storage.read_as_of(object_id, timestamp)

    def query(self, key: str, value) -> List[int]:
        return list(self.index.query(key, value))

    def query_multiple(self, filters: dict):
        if not filters:
            return set()

        result_sets = []

        for key, value in filters.items():
            ids = set(self.query(key, value))
            result_sets.append(ids)

        result = result_sets[0]
        for s in result_sets[1:]:
            result = result.intersection(s)

        return result

    def query_or(self, conditions: list):
        result = set()
        for cond in conditions:
            result |= self.query_multiple(cond)
        return result

    def query_complex(self, query: dict):
        result = None

        if "AND" in query:
            result = self.query_multiple(query["AND"])

        if "OR" in query:
            or_result = self.query_or(query["OR"])

            if result is None:
                result = or_result
            else:
                result = result.intersection(or_result)

        return result if result else set()

    # ✅ ===============================
    # UPDATE (NON-TRANSACTION)
    # ✅ ===============================

    def update_object(self, object_id: int, updates: dict, actor: str, force: bool = False):

        if self.is_stale(object_id):
            raise Exception(f"Object {object_id} is stale. Refresh required.")
        
        lock_key = "__all__"

        if not force:
            if not self.lock_manager.acquire(object_id, lock_key, actor):
                raise Exception(f"Object {object_id} is locked")

        try:
            new_obj, old_obj = self._prepare_object(object_id, updates, actor, force)

            # ✅ inject version
            current_version = self._get_object_version(object_id)
            new_obj["__version"] = current_version + 1
            new_obj["__node_id"] = self.node_id
            new_obj["__txn_id"] = None
            new_obj["__ts"] = time.time()

            binary = self._serialize(new_obj)
            self.storage.append(object_id, binary)
            self._invalidate_transactions(object_id, actor)
            self._update_index(object_id, old_obj, new_obj)

        finally:
            self.lock_manager.release(object_id, lock_key, actor)

    # ✅ ===============================
    # TRANSACTION
    # ✅ ===============================

    def begin_transaction(self, owner: str):
        return Transaction(self, owner)

    def _commit_object(self, object_id, old_obj, new_obj, actor):
        current_version = self._get_object_version(object_id)
        new_obj["__version"] = current_version + 1
        new_obj["__version"] = current_version + 1
        new_obj["__node_id"] = self.node_id
        new_obj["__txn_id"] = getattr(self, "_current_txn_id", None)
        new_obj["__ts"] = time.time()

        binary = self._serialize(new_obj)
        self.storage.append(object_id, binary)
        self._invalidate_transactions(object_id, actor)
        self._update_index(object_id, old_obj, new_obj)

    # ✅ ===============================
    # HELPERS
    # ✅ ===============================

    def _serialize(self, obj: dict) -> bytes:
        return json.dumps(obj).encode()

    def _deserialize(self, data: bytes) -> dict:
        return json.loads(data.decode())

    def _update_index(self, object_id: int, old_obj: dict, new_obj: dict):
        self.index.update(object_id, old_obj, new_obj)

    def _rebuild_index(self):
        all_data = self.storage.read_all()

        for record in all_data:
            obj = self._deserialize(record["data"])
            self.index.update(record["object_id"], {}, obj)

    def _get_object_version(self, object_id):
        data = self.storage.read_latest(object_id)

        if not data:
            return 0

        obj = self._deserialize(data)   # ✅ FIX
        return obj.get("__version", 0)

    # ✅ ===============================
    # OBJECT PREP
    # ✅ ===============================

    def _prepare_object(self, object_id, updates, actor=None, force=False):
        current_data = self.storage.read_latest(object_id)

        if current_data is None:
            obj = {}
        else:
            obj = self._deserialize(current_data)

        # ✅ AUTH
        if actor is not None:
            if not self.auth.can_update(object_id, obj, updates, actor, force):
                raise Exception(f"Unauthorized update on object {object_id}")

        old_obj = obj.copy()

        self._validate_tree_update(object_id, updates)

        for key, value in updates.items():
            if value is DELETE:
                obj.pop(key, None)
            else:
                obj[key] = value

        return obj, old_obj

    # ✅ ===============================
    # TREE
    # ✅ ===============================

    def get_parent(self, object_id):
        data = self.storage.read_latest(object_id)
        if not data:
            return None
        return self._deserialize(data).get("owner")

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
            stack.extend(self.get_children(current))

        return result

    def query_in_subtree(self, root_id, filters: dict):
        return self.get_subtree(root_id).intersection(self.query_multiple(filters))

    def query_complex_in_subtree(self, root_id, query: dict):
        return self.get_subtree(root_id).intersection(self.query_complex(query))

    def _validate_tree_update(self, object_id, updates):
        if "owner" not in updates:
            return

        new_parent = updates["owner"]

        if new_parent is None:
            return

        parent_data = self.storage.read_latest(new_parent)
        if parent_data is None:
            raise Exception(f"Parent {new_parent} does not exist")

        if new_parent == object_id:
            raise Exception("Object cannot be its own parent")

        ancestors = self.get_ancestors(new_parent)

        if object_id in ancestors:
            raise Exception("Cycle detected")

    def update_attribute(self, object_id, attribute, value, owner, force=False):
        self.update_object(object_id, {attribute: value}, owner, force)
    
    def _register_txn(self, object_id, txn):
        if object_id not in self.active_transactions:
            self.active_transactions[object_id] = set()

        self.active_transactions[object_id].add(txn)

    def _invalidate_transactions(self, object_id, actor=None):
        txns = self.active_transactions.get(object_id, set())

        for txn in txns:
            if txn.actor != actor:
                txn.invalidate()

    def _load_or_create_node_id(self, db_path):
        node_file = db_path + ".node"

        if os.path.exists(node_file):
            with open(node_file, "r") as f:
                return f.read().strip()

        node_id = str(uuid.uuid4())

        with open(node_file, "w") as f:
            f.write(node_id)

        return node_id

    def get_changes(self, since_ts: float):
        changes = []

        all_data = self.storage.read_all()

        for record in all_data:
            obj = self._deserialize(record["data"])

            ts = obj.get("__ts", 0)

            if ts > since_ts:
                changes.append({
                    "object_id": record["object_id"],
                    "data": obj
                })

        return changes

    def apply_remote_change(self, object_id: int, obj: dict):
        incoming_version = obj.get("__version", 0)

        # ✅ update node's knowledge (even if not applied)
        self.latest_seen_version[object_id] = max(
            incoming_version,
            self.latest_seen_version.get(object_id, 0)
        )
        current_data = self.read_latest(object_id)

        if current_data:
            current_obj = self._deserialize(current_data)
            current_version = current_obj.get("__version", 0)
            current_ts = current_obj.get("__ts", 0)
        else:
            current_obj = {}
            current_version = 0
            current_ts = 0

        incoming_version = obj.get("__version", 0)
        incoming_ts = obj.get("__ts", 0)

        # ✅ version takes priority
        if incoming_version > current_version:
            should_apply = True

        # ✅ same version → resolve via timestamp
        elif incoming_version == current_version and incoming_ts > current_ts:
            should_apply = True

        else:
            should_apply = False

        if not should_apply:
            return

        # ✅ apply incoming change
        binary = self._serialize(obj)
        self.storage.append(object_id, binary)

        # ✅ update index with proper old → new transition
        self._update_index(object_id, current_obj, obj)

    def is_stale(self, object_id: int):
        local_version = self._get_object_version(object_id)
        known_version = self.latest_seen_version.get(object_id, local_version)

        return local_version < known_version
