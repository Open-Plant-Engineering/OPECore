import json
import os


class WAL:
    def __init__(self, path: str):
        self.path = path + ".wal"

    def log_transaction(self, owner: str, changes: dict):
        entry = {
            "type": "transaction",
            "owner": owner,
            "changes": changes
        }

        with open(self.path, "w") as f:
            f.write(json.dumps(entry))
            f.flush()
            os.fsync(f.fileno())

    def read(self):
        if not os.path.exists(self.path):
            return None

        with open(self.path, "r") as f:
            return json.loads(f.read())

    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)