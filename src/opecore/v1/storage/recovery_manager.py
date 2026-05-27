from opecore.v1.storage.txn_manager import TransactionManager
from opecore.v1.storage.snapshot_manager import SnapshotManager

CHUNK_RECORD = 1
OBJECT_RECORD = 2


class RecoveryManager:
    """
    SOLID v1 RecoveryManager

    Responsibility:
    - Rebuild storage indices from WAL
    - Ignore uncommitted transactions
    """

    def __init__(self, file_manager, chunk_store, object_store):
        self.fm = file_manager
        self.txn_mgr = TransactionManager(file_manager)

        self.chunk = chunk_store
        self.obj = object_store

    # ------------------------
    # RECOVERY ENTRY
    # ------------------------

    def rebuild(self):
        snapshot_mgr = SnapshotManager(self.fm.path)

        snapshot = snapshot_mgr.load()

        committed = self.txn_mgr.recover_committed()

        if snapshot:
            self.chunk.index = snapshot["chunk_index"]
            self.obj.index = snapshot["object_index"]
            start_offset = snapshot["last_offset"]
        else:
            self.chunk.index.clear()
            self.obj.index.clear()
            start_offset = 0

        last_offset = start_offset

        for offset, (rtype, payload) in self.fm.scan_records():
            if offset < start_offset:
                continue

            txn_id = int.from_bytes(payload[:8], "little")

            if txn_id not in committed:
                continue

            data = payload[8:]

            if rtype == CHUNK_RECORD:
                self.chunk.index[data[:32]] = offset

            elif rtype == OBJECT_RECORD:
                oid = int.from_bytes(data[:16], "little")
                self.obj.index[oid] = offset

            last_offset = offset

        # ✅ SAVE SNAPSHOT after rebuild
        snapshot_mgr.save(self.chunk, self.obj, last_offset)

    # ------------------------
    # APPLY LOGIC
    # ------------------------

    def _apply_chunk(self, offset, data):
        chunk_id = data[:32]
        self.chunk.index[chunk_id] = offset

    def _apply_object(self, offset, data):
        object_id = int.from_bytes(data[:16], "little")
        self.obj.index[object_id] = offset

    # ------------------------
    # INTERNAL
    # ------------------------

    def _extract_txn_id(self, payload):
        return int.from_bytes(payload[:8], "little")
