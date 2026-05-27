from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.index.btree import BTree
from opecore.txn.manager import TransactionManager
from opecore.recovery.rebuilder import RecoveryManager
from opecore.compaction.compact import Compactor
from opecore.util.hash import make_sec_key
from opecore.version.store import VersionStore
import gc
import time


class Database:
    def __init__(self, path):
        self.fm = FileManager(path)
        self.txn = TransactionManager(self.fm)

        self.chunk = ChunkStore(self.fm)
        self.obj = ObjectStore(self.fm, self.chunk)
        self.index = BTree(self.fm)
        self.sec_index = BTree(self.fm)

        self.version = VersionStore()

        self.object_versions = {}   # object_id → latest version
        self.version_objects = {}   # version_id → object_id

        # rebuild data
        RecoveryManager(self.fm, self.chunk, self.obj).rebuild()

        # ✅ NEW: rebuild version metadata
        self._rebuild_versions()

    def close(self):
        if self.fm:
            try:
                self.fm.close()
            except:
                pass

        self.chunk = None
        self.obj = None
        self.index = None
        self.sec_index = None
        self.version = None
        self.object_versions = None
        self.version_objects = None

        gc.collect()

    # ✅ INSERT
    def insert(self, data: dict):
        tid = self.txn.begin()

        fields = []

        for k, v in data.items():
            key_chunk = self.chunk.put(k.encode(), tid)
            val_chunk = self.chunk.put(v, tid)
            fields.append((key_chunk, 1, val_chunk))

        obj_id = self.obj.put(fields=fields, txn_id=tid)

        # ✅ create version
        vid = self.version.create(obj_id, parent_version=None)

        self.object_versions[obj_id] = vid
        self.version_objects[vid] = obj_id

        # ✅ persist version metadata
        self._persist_version_meta(tid, vid, obj_id, None)

        # ✅ persist version→object mapping
        self._persist_version_object(tid, vid, obj_id)

        # ✅ primary index
        self.index.insert(obj_id, obj_id, tid)

        # ✅ secondary index
        for k, v in data.items():
            sk = make_sec_key(k, v)

            existing = self.sec_index.search(sk)
            new_val = [obj_id] if existing is None else existing + [obj_id]

            self.sec_index.insert(sk, new_val, tid)

        self.txn.commit(tid)
        return obj_id

    # ✅ UPDATE
    def update(self, object_id, changes: dict):
        tid = self.txn.begin()

        parent = self.object_versions.get(object_id)

        fields = []

        for k, v in changes.items():
            key_chunk = self.chunk.put(k.encode(), tid)
            val_chunk = self.chunk.put(v, tid)
            fields.append((key_chunk, 1, val_chunk))

        new_obj_id = self.obj.put(fields=fields, txn_id=tid)

        vid = self.version.create(object_id, parent_version=parent)

        self.object_versions[object_id] = vid
        self.version_objects[vid] = new_obj_id

        # ✅ persist version metadata
        self._persist_version_meta(tid, vid, object_id, parent)

        # ✅ persist version→object mapping
        self._persist_version_object(tid, vid, new_obj_id)

        # ✅ update secondary index
        for k, v in changes.items():
            sk = make_sec_key(k, v)
            existing = self.sec_index.search(sk)
            new_val = [object_id] if existing is None else existing + [object_id]
            self.sec_index.insert(sk, new_val, tid)

        self.txn.commit(tid)
        return vid

    # ✅ persist version metadata
    def _persist_version_meta(self, tid, vid, object_id, parent):
        parent_val = b"None" if parent is None else str(parent).encode()
        ts = str(self.version.get(vid)["timestamp"]).encode()

        fields = [
            (self.chunk.put(b"kind", tid), 1, self.chunk.put(b"version_meta", tid)),
            (self.chunk.put(b"version_id", tid), 1, self.chunk.put(str(vid).encode(), tid)),
            (self.chunk.put(b"object_id", tid), 1, self.chunk.put(str(object_id).encode(), tid)),
            (self.chunk.put(b"parent", tid), 1, self.chunk.put(parent_val, tid)),
            (self.chunk.put(b"timestamp", tid), 1, self.chunk.put(ts, tid)),
        ]

        self.obj.put(fields=fields, txn_id=tid)

    # ✅ persist version → object mapping
    def _persist_version_object(self, tid, vid, obj_id):
        fields = [
            (self.chunk.put(b"kind", tid), 1, self.chunk.put(b"version_obj", tid)),
            (self.chunk.put(b"version_id", tid), 1, self.chunk.put(str(vid).encode(), tid)),
            (self.chunk.put(b"object_ref", tid), 1, self.chunk.put(str(obj_id).encode(), tid)),
        ]

        self.obj.put(fields=fields, txn_id=tid)

    # ✅ rebuild versions from storage
    def _rebuild_versions(self):
        for obj_id in self.obj.index.keys():
            obj = self.obj.get(obj_id)

            data = {}

            for k, _, v in obj["fields"]:
                key = self.chunk.get(k).decode()
                val = self.chunk.get(v).decode()
                data[key] = val

            if data.get("kind") == "version_meta":
                vid = int(data["version_id"])
                oid = int(data["object_id"])
                parent = None if data["parent"] == "None" else int(data["parent"])
                ts = int(data["timestamp"])

                self.version.versions[vid] = {
                    "node_id": oid,
                    "parent": parent,
                    "timestamp": ts,
                }

                self.object_versions[oid] = vid

            elif data.get("kind") == "version_obj":
                vid = int(data["version_id"])
                oid = int(data["object_ref"])
                self.version_objects[vid] = oid

    # ✅ resolve chain
    def _resolve(self, object_id, version_id):
        result = {}
        visited = set()

        while version_id:
            if version_id in visited:
                break
            visited.add(version_id)

            obj_id = self.version_objects.get(version_id)

            if obj_id:
                obj = self.obj.get(obj_id)

                for k, _, v in obj["fields"]:
                    key = self.chunk.get(k).decode()
                    val = self.chunk.get(v)

                    if key not in result:
                        result[key] = val

            meta = self.version.get(version_id)
            version_id = meta["parent"] if meta else None

        return result

    def get(self, object_id):
        vid = self.object_versions.get(object_id)
        return None if vid is None else self._resolve(object_id, vid)

    def get_as_of(self, object_id, timestamp):
        vid = self.object_versions.get(object_id)

        while vid:
            meta = self.version.get(vid)

            if meta and meta["timestamp"] <= timestamp:
                return self._resolve(object_id, vid)

            vid = meta["parent"] if meta else None

        return None

    def get_versions(self, object_id):
        versions = []
        vid = self.object_versions.get(object_id)

        while vid:
            versions.append(vid)
            meta = self.version.get(vid)
            vid = meta["parent"] if meta else None

        return versions

    def scan(self):
        return [(obj_id, self.get(obj_id)) for obj_id in self.obj.index.keys()]

    def find(self, field, value):
        key = make_sec_key(field, value)
        return self.sec_index.search(key) or []

    def compact(self):
        Compactor(self).compact()

    def range(self, start_id, end_id):
        return self.index.range(start_id, end_id)
