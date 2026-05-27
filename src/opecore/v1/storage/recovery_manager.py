from opecore.v1.storage.txn_manager import TransactionManager

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
        committed = self.txn_mgr.recover_committed()

        # reset indexes
        self.chunk.index.clear()
        self.obj.index.clear()

        for offset, (rtype, payload) in self.fm.scan_records():
            txn_id = self._extract_txn_id(payload)

            if txn_id not in committed:
                continue

            data = payload[8:]  # skip txn_id

            if rtype == CHUNK_RECORD:
                self._apply_chunk(offset, data)

            elif rtype == OBJECT_RECORD:
                self._apply_object(offset, data)

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
