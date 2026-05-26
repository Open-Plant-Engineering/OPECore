import os
import json


class WAL:
    def __init__(self, path):
        self.path = path

        if not os.path.exists(path):
            open(path, "a").close()

    def _append(self, record):
        with open(self.path, "a") as f:
            f.write(json.dumps(record) + "\n")
            f.flush()
            os.fsync(f.fileno())

    def log_prepare(self, txn_id, changes):
        record = {
            "txn_id": txn_id,
            "state": "PREPARE",
            "changes": changes
        }
        self._append(record)

    def log_commit(self, txn_id):
        record = {
            "txn_id": txn_id,
            "state": "COMMIT"
        }
        self._append(record)

    # ✅ backward compatibility for tests
    def log_transaction(self, txn_id, changes):
        self.log_prepare(txn_id, changes)
        self.log_commit(txn_id)

    def read_all(self):
        if not os.path.exists(self.path):
            return []

        records = []

        with open(self.path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))

        return records

    def clear(self):
        open(self.path, "w").close()