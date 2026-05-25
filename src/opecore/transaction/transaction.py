from typing import Dict
from opecore.core.constants import DELETE


class Transaction:
    """
    Multi-object transaction.
    """

    def __init__(self, engine, owner: str):
        self.engine = engine
        self.owner = owner

        # staged updates
        self.changes: Dict[int, dict] = {}

        self.active = True

    # ✅ ===============================
    # STAGE UPDATE
    # ✅ ===============================

    def update(self, object_id: int, updates: dict):
        if not self.active:
            raise Exception("Transaction is closed")

        if object_id not in self.changes:
            self.changes[object_id] = {}

        self.changes[object_id].update(updates)

    # ✅ ===============================
    # COMMIT
    # ✅ ===============================

    def commit(self):
        if not self.active:
            raise Exception("Transaction already closed")
    
        locked_objects = []
    
        try:
            # ✅ STEP 1: lock ALL objects
            for object_id in self.changes:
                if not self.engine.lock_manager.acquire(object_id, "__all__", self.owner):
                    raise Exception(f"Failed to lock {object_id}")
    
                locked_objects.append(object_id)
    
            # ✅ STEP 2: PREPARE everything (NO writes yet)
            prepared = []
    
            for object_id, updates in self.changes.items():
                new_obj, old_obj = self.engine._prepare_object(object_id, updates)
                prepared.append((object_id, old_obj, new_obj))
    
            # ✅ STEP 3: COMMIT all at once
            for object_id, old_obj, new_obj in prepared:
                self.engine._commit_object(object_id, old_obj, new_obj)
    
            self.active = False
    
        finally:
            # ✅ STEP 4: release locks
            for object_id in locked_objects:
                self.engine.lock_manager.release(object_id, "__all__", self.owner)

    # ✅ ===============================
    # ROLLBACK
    # ✅ ===============================

    def rollback(self):
        self.changes.clear()
        self.active = False