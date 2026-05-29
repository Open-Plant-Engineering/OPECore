import json
import os
from opecore.storage.safe import safe_write


class NameIndex:
    def __init__(self, path: str):
        self.path = path

        if not os.path.exists(path):
            safe_write(path, json.dumps({}).encode())

    def _load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def _save(self, data):
        safe_write(self.path, json.dumps(data, indent=2).encode())

    # ✅ Add entry
    def put(self, name: str, refno: str):
        data = self._load()

        if name in data:
            raise ValueError(f"Name already exists: {name}")

        data[name] = refno
        self._save(data)

    # ✅ Get refno
    def get(self, name: str):
        data = self._load()
        return data.get(name)

    # ✅ Remove entry
    def remove(self, name: str):
        data = self._load()

        if name in data:
            del data[name]
            self._save(data)

    # ✅ Exists
    def exists(self, name: str):
        data = self._load()
        return name in data
