import json
import os
from opecore.storage.safe import safe_write


class GenericIndex:
    def __init__(self, path: str):
        self.path = path

        if not os.path.exists(path):
            safe_write(path, json.dumps({}).encode())

    def _load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def _save(self, data):
        safe_write(self.path, json.dumps(data, indent=2).encode())

    # ✅ add mapping
    def add(self, attr, value, refno):
        data = self._load()

        if attr not in data:
            data[attr] = {}

        if value not in data[attr]:
            data[attr][value] = []

        if refno not in data[attr][value]:
            data[attr][value].append(refno)

        self._save(data)

    # ✅ remove mapping
    def remove(self, attr, value, refno):
        data = self._load()
    
        if attr in data and value in data[attr]:
            if refno in data[attr][value]:
                data[attr][value].remove(refno)
    
                # ✅ cleanup empty list
                if not data[attr][value]:
                    del data[attr][value]
    
            # ✅ cleanup empty attr
            if not data[attr]:
                del data[attr]
    
        self._save(data)

    # ✅ lookup
    def get(self, attr, value):
        data = self._load()

        if attr in data and value in data[attr]:
            return data[attr][value]

        return []