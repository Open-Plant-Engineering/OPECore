import json
import os


class WAL:
    """
    Simple Write-Ahead Log.
    """

    def __init__(self, path: str):
        self.path = path + ".wal"

    # ✅ write log before actual write
    def log(self, object_id: int, data: bytes):
        entry = {
            "object_id": object_id,
            "data": data.decode()
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()
            os.fsync(f.fileno())  # ✅ ensure disk write

    # ✅ read WAL entries
    def read_all(self):
        if not os.path.exists(self.path):
            return []

        entries = []
        with open(self.path, "r") as f:
            for line in f:
                entries.append(json.loads(line.strip()))

        return entries

    # ✅ clear WAL after commit
    def clear(self):
        if os.path.exists(self.path):
            os.remove(self.path)