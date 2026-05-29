import json
import os
import uuid
from opecore.storage.safe import safe_write


class ChunkStore:
    def __init__(self, path: str):
        self.path = path

        # ✅ initialize empty store
        if not os.path.exists(path):
            safe_write(path, json.dumps({}).encode())

    def _load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def _save(self, data):
        safe_write(self.path, json.dumps(data, indent=2).encode())

    # ✅ MAIN API

    def put(self, dtype: str, value):
        """
        Store a typed value and return chunk_id
        """

        data = self._load()

        # ✅ simple deduplication
        for cid, entry in data.items():
            if entry["type"] == dtype and entry["value"] == value:
                return cid

        # ✅ create new chunk
        cid = str(uuid.uuid4())

        data[cid] = {
            "type": dtype,
            "value": value
        }

        self._save(data)

        return cid

    def get(self, cid: str):
        """
        Retrieve (type, value)
        """
        data = self._load()

        entry = data.get(cid)
        if not entry:
            return None

        return entry["type"], entry["value"]

    def exists(self, cid: str):
        data = self._load()
        return cid in data

    def all(self):
        return self._load()