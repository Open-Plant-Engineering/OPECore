from opecore.txn.manager import TransactionManager

# record types
CHUNK_RECORD = 1
OBJECT_RECORD = 2
INDEX_PAGE = 5


class RecoveryManager:
    def __init__(self, fm, chunk_store, object_store):
        self.fm = fm
        self.txn_mgr = TransactionManager(fm)

        self.chunk_store = chunk_store
        self.object_store = object_store

    def rebuild(self):
        committed = self.txn_mgr.recover_committed()

        # clear current in-memory indexes
        self.chunk_store.index.clear()
        self.object_store.index.clear()

        for offset, (rtype, payload) in self.fm.scan_records():
            txn_id = int.from_bytes(payload[:8], "little")

            # ✅ ignore uncommitted data
            if txn_id not in committed:
                continue

            data = payload[8:]

            if rtype == CHUNK_RECORD:
                self._apply_chunk(offset, data)

            elif rtype == OBJECT_RECORD:
                self._apply_object(offset, data)

            # index pages already handled via root pointer

    def _apply_chunk(self, offset, data):
        chunk_id = data[:32]
        self.chunk_store.index[chunk_id] = offset

    def _apply_object(self, offset, data):
        object_id = int.from_bytes(data[:16], "little")
        self.object_store.index[object_id] = offset
