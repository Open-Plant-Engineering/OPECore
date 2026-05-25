from typing import Dict
from opecore.core.constants import DELETE


class Transaction:
    """
    Multi-object transaction.
    """

    def __init__(self, engine, actor: str):
        self.engine = engine
        self.actor = actor

        # staged updates
        self.changes: Dict[int, dict] = {}

        self.snapshot_versions = {}

        self.active = True

    # ✅ ===============================
    # STAGE UPDATE
    # ✅ ===============================

    def update(self, object_id: int, updates: dict):
        if not self.active:
            raise Exception("Transaction is closed")

        if object_id not in self.changes:
            self.changes[object_id] = {}
            
            self.snapshot_versions[object_id] = self.engine._get_object_version(object_id)

        self.changes[object_id].update(updates)

    # ✅ ===============================
    # COMMIT
    # ✅ ===============================

    def commit(self):
        if not self.active:
            raise Exception("Transaction already closed")

        locked_objects = []

        try:
            prepared = []

            # ✅ STEP 1: VALIDATION FIRST
            for object_id, updates in self.changes.items():
            
                # ✅ STEP A: current version
                current_version = self.engine._get_object_version(object_id)

                original_version = self.snapshot_versions.get(object_id)

                # ✅ STEP B: detect change
                if original_version != current_version:
                    # ✅ re-check ownership before failing
                    current_data = self.engine.storage.read_latest(object_id)
                
                    if current_data is not None:
                        current_obj = self.engine._deserialize(current_data)
                    else:
                        current_obj = {}
                
                    claim_by = current_obj.get("claim_by")
                
                    # ❌ ONLY fail if ownership changed
                    if claim_by is None or claim_by != self.actor:
                        raise Exception(f"Object {object_id} changed during transaction")

                # ✅ STEP C: proceed
                new_obj, old_obj = self.engine._prepare_object(
                    object_id, updates, self.actor
                )

                prepared.append((object_id, old_obj, new_obj))

            # ✅ STEP 2: lock ALL
            for object_id in self.changes:
                if not self.engine.lock_manager.acquire(object_id, "__all__", self.actor):
                    raise Exception(f"Failed to lock {object_id}")

                locked_objects.append(object_id)
                
            # ✅ STEP 2.5: RE-VALIDATE after lock (CRITICAL)
            for object_id in self.changes:
                current_data = self.engine.storage.read_latest(object_id)

                if current_data is not None:
                    current_obj = self.engine._deserialize(current_data)
                else:
                    current_obj = {}

                claim_by = current_obj.get("claim_by")

                if claim_by is not None and claim_by != self.actor:
                    raise Exception(f"Object {object_id} lost ownership before commit")

            # ✅ STEP 3: WAL LOG (CRITICAL)
            self.engine.storage.wal.log_transaction(self.actor, self.changes)

            # ✅ STEP 4: APPLY writes
            for object_id, old_obj, new_obj in prepared:
                self.engine._commit_object(object_id, old_obj, new_obj)

            # ✅ STEP 5: CLEAR WAL
            self.engine.storage.wal.clear()

            self.active = False

        finally:
            for object_id in locked_objects:
                self.engine.lock_manager.release(object_id, "__all__", self.actor)

    # ✅ ===============================
    # ROLLBACK
    # ✅ ===============================

    def rollback(self):
        self.changes.clear()
        self.active = False