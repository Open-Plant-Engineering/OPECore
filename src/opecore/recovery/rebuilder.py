from opecore.txn.manager import TransactionManager
from opecore.recovery.snapshot import SnapshotManager

# record types
CHUNK_RECORD = 1
OBJECT_RECORD = 2
INDEX_PAGE = 5


class RecoveryManager:
    def __init__(self, fm, chunk_store, object_store):
        self.fm = fm
        self.txn_mgr = TransactionManager(fm)
        self.snapshot_mgr = SnapshotManager(fm)

        self.chunk_store = chunk_store
        self.object_store = object_store

    def rebuild(self):
        committed = self.txn_mgr.recover_committed()

        snapshot = self.snapshot_mgr.load_latest()

        if snapshot:
            self.chunk_store.index = snapshot["chunk_index"]
            self.object_store.index = snapshot["object_index"]
            start_offset = snapshot["last_offset"]
        else:
            self.chunk_store.index.clear()
            self.object_store.index.clear()
            start_offset = 0

        for offset, (rtype, payload) in self.fm.scan_records():
            if offset < start_offset:
                continue

            txn_id = int.from_bytes(payload[:8], "little")

            # ✅ ignore uncommitted data
            if txn_id not in committed:
                continue

            data = payload[8:]

            if rtype == CHUNK_RECORD:
                chunk_id = data[:32]
                self.chunk_store.index[chunk_id] = offset

            elif rtype == OBJECT_RECORD:
                object_id = int.from_bytes(data[:16], "little")
                self.object_store.index[object_id] = offset

            # index pages already handled via root pointer

    def _apply_chunk(self, offset, data):
        chunk_id = data[:32]
        self.chunk_store.index[chunk_id] = offset

    def _apply_object(self, offset, data):
        object_id = int.from_bytes(data[:16], "little")
        self.object_store.index[object_id] = offset
