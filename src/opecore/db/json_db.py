import json
import os
from opecore.storage.safe import safe_write
from opecore.model.node import Node


class JsonDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

        if not os.path.exists(db_path):
            safe_write(db_path, json.dumps({"nodes": {}}).encode())

    def load(self):
        with open(self.db_path, "r") as f:
            return json.load(f)

    def save(self, data):
        safe_write(self.db_path, json.dumps(data, indent=2).encode())

    # ✅ CREATE
    def create_node(self, node: Node):
        db = self.load()

        if node.refno in db["nodes"]:
            raise ValueError("Node already exists")

        db["nodes"][node.refno] = node.to_dict()

        self.save(db)
        return node.refno

    # ✅ READ
    def get_node(self, refno: str):
        db = self.load()
        data = db["nodes"].get(refno)

        if not data:
            return None

        return Node.from_dict(data)

    # ✅ UPDATE
    def update_node(self, node: Node):
        db = self.load()

        if node.refno not in db["nodes"]:
            raise ValueError("Node not found")

        db["nodes"][node.refno] = node.to_dict()

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
        return [Node.from_dict(n) for n in db["nodes"].values()]
