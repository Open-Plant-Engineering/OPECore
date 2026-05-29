import json
import os
from opecore.storage.safe import safe_write
from opecore.model.node import Node


class JsonDB:
    def __init__(self, db_path: str, chunk_store, name_index):
        self.db_path = db_path
        self.chunk_store = chunk_store
        self.name_index = name_index

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

        # ✅ extract name
        name = node.attributes.get("name")

        if name:
            if self.name_index.exists(name):
                raise ValueError(f"Duplicate name: {name}")

        encoded = self._encode_attributes(node.attributes)

        if node.refno in db["nodes"]:
            raise ValueError("Node already exists")

        db["nodes"][node.refno] = encoded

        self.save(db)

        # ✅ update index AFTER successful write
        if name:
            self.name_index.put(name, node.refno)

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

        old_node = self.get_node(node.refno)

        old_name = old_node.attributes.get("name")
        new_name = node.attributes.get("name")

        # ✅ name change
        if old_name != new_name:
            if new_name and self.name_index.exists(new_name):
                raise ValueError(f"Duplicate name: {new_name}")

            if old_name:
                self.name_index.remove(old_name)

            if new_name:
                self.name_index.put(new_name, node.refno)

        encoded = self._encode_attributes(node.attributes)

        db["nodes"][node.refno] = encoded

        self.save(db)

    # ✅ DELETE
    def delete_node(self, refno: str):
        db = self.load()

        node = self.get_node(refno)

        if node:
            name = node.attributes.get("name")
            if name:
                self.name_index.remove(name)

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

    def get_by_name(self, name: str):
        refno = self.name_index.get(name)
    
        if not refno:
            return None
    
        return self.get_node(refno)