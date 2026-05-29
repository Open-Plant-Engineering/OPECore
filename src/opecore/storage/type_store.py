import json
import os
from opecore.storage.safe import safe_write


class TypeStore:
    def __init__(self, path: str):
        self.path = path

        if not os.path.exists(path):
            safe_write(path, json.dumps({}).encode())

    def _load(self):
        with open(self.path, "r") as f:
            return json.load(f)

    def _save(self, data):
        safe_write(self.path, json.dumps(data, indent=2).encode())

    # ✅ register type schema
    def create_type(self, name: str, attributes: dict):
        """
        attributes: { attr_name: dtype }
        Example:
            {
              "name": "string",
              "diameter": "real"
            }
        """
        data = self._load()

        if name in data:
            raise ValueError(f"Type already exists: {name}")

        data[name] = attributes
        self._save(data)

    def get_type(self, name: str):
        data = self._load()
        return data.get(name)

    def exists(self, name: str):
        data = self._load()
        return name in data

    def all_types(self):
        return self._load()