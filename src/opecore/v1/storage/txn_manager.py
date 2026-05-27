import uuid
import struct


TXN_BEGIN = 7
TXN_COMMIT = 8


class TransactionManager:
    """
    SOLID v1 TransactionManager

    Responsibility:
    - Manage transaction lifecycle
    - Write BEGIN / COMMIT records
    - Recover committed transactions

    Does NOT:
    - control business logic
    - manage objects/chunks
    """

    def __init__(self, file_manager):
        self.fm = file_manager

    # ------------------------
    # TRANSACTION API
    # ------------------------

    def begin(self) -> int:
        txn_id = self._new_txn_id()

        payload = struct.pack("<Q", txn_id)

        self.fm.append_record(TXN_BEGIN, payload)

        return txn_id

    def commit(self, txn_id: int):
        payload = struct.pack("<Q", txn_id)

        self.fm.append_record(TXN_COMMIT, payload)

    # ------------------------
    # RECOVERY SUPPORT
    # ------------------------

    def recover_committed(self):
        """
        Returns set of committed txn_ids
        """
        begun = set()
        committed = set()

        for _, (rtype, payload) in self.fm.scan_records():
            txn_id = struct.unpack("<Q", payload[:8])[0]

            if rtype == TXN_BEGIN:
                begun.add(txn_id)

            elif rtype == TXN_COMMIT:
                if txn_id in begun:
                    committed.add(txn_id)

        return committed

    # ------------------------
    # INTERNAL
    # ------------------------

    def _new_txn_id(self):
        # 64-bit txn id
        return uuid.uuid4().int & ((1 << 64) - 1)
