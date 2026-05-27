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

        # ✅ NEW
        self.version = VersionStore()

        # ✅ NEW: object_id → latest version_id
        self.object_versions = {}
        self.version_objects = {}

        # ✅ rebuild state
        RecoveryManager(self.fm, self.chunk, self.obj).rebuild()

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

        gc.collect()

    # ✅ INSERT OBJECT (Versioned)
    def insert(self, data: dict):
        tid = self.txn.begin()

        # ✅ create object first
        obj_id = None

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

        # ✅ primary index
        self.index.insert(obj_id, obj_id, tid)

        # ✅ secondary index
        for k, v in data.items():
            sk = make_sec_key(k, v)

            existing = self.sec_index.search(sk)

            if existing is None:
                new_val = [obj_id]
            else:
                new_val = existing + [obj_id]

            self.sec_index.insert(sk, new_val, tid)

        self.txn.commit(tid)

        return obj_id

    # ✅ UPDATE OBJECT (creates new version)
    def update(self, object_id, changes: dict):
        tid = self.txn.begin()

        parent = self.object_versions.get(object_id)

        # ✅ build ONLY changed fields
        fields = []
        for k, v in changes.items():
            key_chunk = self.chunk.put(k.encode(), tid)
            val_chunk = self.chunk.put(v, tid)
            fields.append((key_chunk, 1, val_chunk))

        # ✅ store delta object
        new_obj_id = self.obj.put(fields=fields, txn_id=tid)

        # ✅ new version
        vid = self.version.create(object_id, parent_version=parent)
        self.object_versions[object_id] = vid
        self.version_objects[vid] = new_obj_id

        # ✅ secondary index update
        for k, v in changes.items():
            sk = make_sec_key(k, v)

            existing = self.sec_index.search(sk)

            if existing is None:
                new_val = [object_id]
            else:
                new_val = existing + [object_id]

            self.sec_index.insert(sk, new_val, tid)

        self.txn.commit(tid)

        return vid

    # ✅ INTERNAL RESOLVE (version chain)
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

    # ✅ GET OBJECT (latest version)
    def get(self, object_id):
        vid = self.object_versions.get(object_id)

        if vid is None:
            return None

        return self._resolve(object_id, vid)

    # ✅ GET AS OF (time travel)
    def get_as_of(self, object_id, timestamp):
        vid = self.object_versions.get(object_id)

        while vid:
            meta = self.version.get(vid)

            if meta and meta["timestamp"] <= timestamp:
                return self._resolve(object_id, vid)

            vid = meta["parent"] if meta else None

        return None

    # ✅ GET VERSION LIST
    def get_versions(self, object_id):
        versions = []

        vid = self.object_versions.get(object_id)

        while vid:
            versions.append(vid)
            meta = self.version.get(vid)
            vid = meta["parent"] if meta else None

        return versions

    # ✅ SCAN (latest state)
    def scan(self):
        results = []

        for obj_id in self.obj.index.keys():
            results.append((obj_id, self.get(obj_id)))

        return results

    # ✅ FIND (uses secondary index)
    def find(self, field, value):
        key = make_sec_key(field, value)

        result = self.sec_index.search(key)

        return result or []

    def compact(self):
        Compactor(self).compact()

    def range(self, start_id, end_id):
        return self.index.range(start_id, end_id)
