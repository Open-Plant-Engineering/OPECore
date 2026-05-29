import json
import os
from opecore.storage.safe import safe_write
from opecore.model.node import Node


class DBEngine:
    def __init__(self, db_path, chunk_store, name_index, type_store, generic_index):
        self.db_path = db_path
        self.chunk_store = chunk_store
        self.name_index = name_index
        self.type_store = type_store
        self.generic_index = generic_index

        if not os.path.exists(db_path):
            safe_write(db_path, json.dumps({"nodes": {}}).encode())

    def load(self):
        with open(self.db_path, "r") as f:
            return json.load(f)

    def save(self, data):
        safe_write(self.db_path, json.dumps(data, indent=2).encode())

    # ✅ Helper — detect type
    def _detect_type(self, value, expected_type=None):
        if expected_type == "ref":
            return "ref"

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

        node_type = attrs.get("type")
        schema = self.type_store.get_type(node_type) if node_type else {}

        for k, v in attrs.items():
            if k == "refno":
                encoded[k] = v
            else:
                expected = schema.get(k) if schema else None

                dtype = self._detect_type(v, expected)
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

        self._validate_against_type(node.attributes)
        self._validate_relationships(node.attributes)
        encoded = self._encode_attributes(node.attributes)

        if node.refno in db["nodes"]:
            raise ValueError("Node already exists")

        db["nodes"][node.refno] = encoded

        self.save(db)

        # ✅ update index AFTER successful write
        if name:
            self.name_index.put(name, node.refno)

        # ✅ add to generic index
        for k, v in node.attributes.items():
            if k in ["refno", "name"] or v is None:
                continue
            
            self.generic_index.add(k, v, node.refno)

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

        # ✅ merge attributes (optional but recommended)
        merged_attrs = old_node.attributes.copy()
        merged_attrs.update(node.attributes)
        node.attributes = merged_attrs

        # ✅ name validation
        if old_name != new_name:
            if new_name and self.name_index.exists(new_name):
                raise ValueError(f"Duplicate name: {new_name}")

        # ✅ validate FIRST
        self._validate_against_type(node.attributes)
        self._validate_relationships(node.attributes)

        # ✅ update name index AFTER validation
        if old_name != new_name:
            if old_name:
                self.name_index.remove(old_name)
            if new_name:
                self.name_index.put(new_name, node.refno)

        # ✅ remove old generic index
        for k, v in old_node.attributes.items():
            if k in ["refno", "name"] or v is None:
                continue

            self.generic_index.remove(k, v, node.refno)

        # ✅ encode + save
        encoded = self._encode_attributes(node.attributes)
        db["nodes"][node.refno] = encoded
        self.save(db)

        # ✅ add new generic index
        for k, v in node.attributes.items():
            if k in ["refno", "name"] or v is None:
                continue

            self.generic_index.add(k, v, node.refno)

    # ✅ DELETE
    def delete_node(self, refno: str):
        db = self.load()

        node = self.get_node(refno)

        # ✅ remove from generic index
        if node:
            for k, v in node.attributes.items():
                if k in ["refno", "name"] or v is None:
                    continue
                
                self.generic_index.remove(k, v, refno)

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

    def _validate_against_type(self, attrs: dict):
        node_type = attrs.get("type")

        if not node_type:
            return  # no type, skip validation

        schema = self.type_store.get_type(node_type)

        if not schema:
            raise ValueError(f"Unknown type: {node_type}")

        for k, v in attrs.items():
            if k in ["refno", "type"]:
                continue

            expected = schema.get(k)

            if not expected:
                raise ValueError(f"Attribute not allowed: {k}")

            actual = self._detect_type(v, expected_type=expected)

            if actual != expected:
                raise ValueError(
                    f"Type mismatch for '{k}': expected {expected}, got {actual}"
                )

    def _node_exists(self, refno):
        db = self.load()
        return refno in db["nodes"]

    def _validate_relationships(self, attrs: dict):
        refno = attrs.get("refno")

        # ✅ Rule 3: no self-parent
        parent = attrs.get("parent")
        if parent:
            if parent == refno:
                raise ValueError("Node cannot be parent of itself")

            if not self._node_exists(parent):
                raise ValueError(f"Parent does not exist: {parent}")

        # ✅ Rule 1: owner must exist
        owner = attrs.get("owner")
        if owner:
            if not self._node_exists(owner):
                raise ValueError(f"Owner does not exist: {owner}")

        # ✅ Rule 2: validate all REF attributes from schema
        node_type = attrs.get("type")
        if not node_type:
            return

        schema = self.type_store.get_type(node_type)
        if not schema:
            return

        for attr_name, dtype in schema.items():
            if dtype == "ref":
                ref_value = attrs.get(attr_name)

                # ✅ allowed: missing or None → treated as root/no link
                if not ref_value:
                    continue

                if not self._node_exists(ref_value):
                    raise ValueError(
                        f"Invalid reference in '{attr_name}': {ref_value}"
                    )
