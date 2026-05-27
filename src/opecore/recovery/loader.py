from opecore.txn.manager import TransactionManager


class RecoveryLoader:
    def __init__(self, fm):
        self.fm = fm
        self.txn_mgr = TransactionManager(fm)

    def load(self):
        committed = self.txn_mgr.recover_committed()

        valid_records = []

        for offset, (rtype, payload) in self.fm.scan_records():
            txn_id = int.from_bytes(payload[:8], "little")

            if txn_id in committed:
                valid_records.append((offset, rtype, payload[8:]))

        return valid_records
