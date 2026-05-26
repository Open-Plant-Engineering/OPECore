from typing import Dict
from opecore.core.constants import DELETE


class Transaction:
    """
    Multi-object transaction.
    """

    def __init__(self, engine, actor: str):
        self.engine = engine
        self.actor = actor

        self.changes: Dict[int, dict] = {}
        self.snapshot_versions = {}

        self.active = True
        self.txn_id = None

    # ✅ ===============================
    # STAGE UPDATE
    # ✅ ===============================

    def update(self, object_id: int, updates: dict):
        if not self.active:
            raise Exception("Transaction is closed")

        if object_id not in self.changes:
            self.changes[object_id] = {}

            # ✅ snapshot version capture
            self.snapshot_versions[object_id] = self.engine._get_object_version(object_id)

        self.changes[object_id].update(updates)

    # ✅ ===============================
    # COMMIT
    # ✅ ===============================

    def commit(self):
        if not self.active:
            raise Exception("Transaction already closed")

        import uuid, time

        self.txn_id = str(uuid.uuid4())

        # ✅ STEP 1: acquire global write lock
        for _ in range(50):
            if self.engine.file_lock.acquire(self.actor, self.txn_id):
                break
            time.sleep(0.1)
        else:
            raise Exception("Database is busy")

        try:
            prepared = []

            # ✅ STEP 2: VALIDATION + VERSION CHECK
            for object_id, updates in self.changes.items():

                # ✅ version conflict detection (CRITICAL)
                current_version = self.engine._get_object_version(object_id)
                snapshot_version = self.snapshot_versions[object_id]

                if current_version != snapshot_version:
                    raise Exception(f"Conflict detected on object {object_id}")

                new_obj, old_obj = self.engine._prepare_object(
                    object_id, updates, self.actor
                )

                prepared.append((object_id, old_obj, new_obj))

            # ✅ STEP 3: WAL PREPARE (must be first durable step)
            self.engine.storage.wal.log_prepare(self.txn_id, self.changes)

            # ✅ STEP 4: APPLY CHANGES
            for object_id, old_obj, new_obj in prepared:
                self.engine._commit_object(object_id, old_obj, new_obj)

            # ✅ STEP 5: WAL COMMIT
            self.engine.storage.wal.log_commit(self.txn_id)

            self.active = False

        finally:
            # ✅ release lock safely
            try:
                self.engine.file_lock.release(self.actor, self.txn_id)
            except Exception:
                pass

    # ✅ ===============================
    # ROLLBACK
    # ✅ ===============================

    def rollback(self):
        self.changes.clear()
        self.active = False
