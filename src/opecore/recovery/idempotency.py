import os
import json
from opecore.storage.safe import safe_write


class IdempotencyStore:
    def __init__(self, db_path: str):
        self.file = os.path.join(db_path, "processed.json")

        if not os.path.exists(self.file):
            safe_write(self.file, b"[]")

        # ✅ load once into memory
        self._ids = self._load()

    def _load(self):
        with open(self.file, "r") as f:
            return set(json.load(f))

    def _save(self):
        data = json.dumps(list(self._ids)).encode()
        safe_write(self.file, data)

    def is_processed(self, request_id: str) -> bool:
        return request_id in self._ids

    def mark_processed(self, request_id: str):
        # ✅ update in-memory immediately
        if request_id in self._ids:
            return

        self._ids.add(request_id)
        self._save()
