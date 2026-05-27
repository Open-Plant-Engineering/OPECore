import struct
import uuid

TXN_BEGIN = 7
TXN_COMMIT = 8


class TransactionManager:
    def __init__(self, fm):
        self.fm = fm

    def begin(self):
        txn_id = uuid.uuid4().int & ((1 << 64) - 1)

        payload = struct.pack("<Q", txn_id)
        self.fm.append_record(TXN_BEGIN, payload)

        return txn_id

    def commit(self, txn_id):
        payload = struct.pack("<Q", txn_id)
        self.fm.append_record(TXN_COMMIT, payload)

    def recover_committed(self):
        """
        Returns set of committed txn_ids
        """
        begun = set()
        committed = set()

        for _, (rtype, payload) in self.fm.scan_records():
            txn_id = struct.unpack("<Q", payload)[0]

            if rtype == TXN_BEGIN:
                begun.add(txn_id)

            elif rtype == TXN_COMMIT:
                if txn_id in begun:
                    committed.add(txn_id)

        return committed
