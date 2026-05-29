import json
import os
from opecore.storage.safe import safe_write
from opecore.model.node import Node


class JsonDB:
    def __init__(self, db_path: str, chunk_store):
        self.db_path = db_path
        self.chunk_store = chunk_store

        if not os.path.exists(db_path):
            safe_write(db_path, json.dumps({"nodes": {}}).encode())

    def load(self):
        with open(self.db_path, "r") as f:
            return json.load(f)

    def save(self, data):
        safe_write(self.db_path, json.dumps(data, indent=2).encode())

    # ✅ Helper — detect type
    def _detect_type(self, value):
        if isinstance(value, bool):
            return "bool"
        elif isinstance(value, (int, float)):
            return "real"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, str):
            return "string"
        else:
            return "string"

    # ✅ convert attributes → chunk IDs
    def _encode_attributes(self, attrs: dict):
        encoded = {}

        for k, v in attrs.items():
            if k == "refno":
                encoded[k] = v
            else:
                dtype = self._detect_type(v)
                cid = self.chunk_store.put(dtype, v)
                encoded[k] = cid

        return encoded

    # ✅ convert chunk IDs → values
    def _decode_attributes(self, attrs: dict):
        decoded = {}

        for k, v in attrs.items():
            if k == "refno":
                decoded[k] = v
            else:
                result = self.chunk_store.get(v)
                if result:
                    _, value = result
                    decoded[k] = value
                else:
                    decoded[k] = None

        return decoded

    # ✅ CREATE
    def create_node(self, node: Node):
        db = self.load()

        encoded = self._encode_attributes(node.attributes)

        if node.refno in db["nodes"]:
            raise ValueError("Node already exists")

        db["nodes"][node.refno] = encoded

        self.save(db)
        return node.refno

    # ✅ READ
    def get_node(self, refno: str):
        db = self.load()
        data = db["nodes"].get(refno)

        if not data:
            return None

        decoded = self._decode_attributes(data)

        return Node.from_dict(decoded)

    # ✅ UPDATE
    def update_node(self, node: Node):
        db = self.load()

        if node.refno not in db["nodes"]:
            raise ValueError("Node not found")

        encoded = self._encode_attributes(node.attributes)

        db["nodes"][node.refno] = encoded

        self.save(db)

    # ✅ DELETE
    def delete_node(self, refno: str):
        db = self.load()

        if refno in db["nodes"]:
            del db["nodes"][refno]

        self.save(db)

    # ✅ LIST
    def list_nodes(self):
        db = self.load()

        result = []
        for data in db["nodes"].values():
            decoded = self._decode_attributes(data)
            result.append(Node.from_dict(decoded))

        return result
