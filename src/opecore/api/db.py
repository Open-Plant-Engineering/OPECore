from opecore.storage.engine.storage_engine import StorageEngine
from opecore.util.hash import make_sec_key
from opecore.domain.versioning.version_manager import VersionManager


class Database:
    def __init__(self, path):
        self.storage = StorageEngine(path)
        self.vm = VersionManager()

        self._rebuild_versions()

    # ✅ ensure file gets closed (fixes Windows PermissionError)
    def __del__(self):
        try:
            self.close()
        except:
            pass

    def close(self):
        if self.storage:
            self.storage.close()

        self.vm = None

    # ✅ INSERT
    def insert(self, data: dict):
        tid = self.storage.txn.begin()

        fields = []

        for k, v in data.items():
            key_chunk = self.storage.chunk.put(k.encode(), tid)
            val_chunk = self.storage.chunk.put(v, tid)
            fields.append((key_chunk, 1, val_chunk))

        obj_id = self.storage.obj.put(fields=fields, txn_id=tid)

        # ✅ version manager handles version creation
        vid = self.vm.create_version(obj_id, None, obj_id)

        self._persist_version_meta(tid, vid, obj_id, None)
        self._persist_version_object(tid, vid, obj_id)

        self.storage.index.insert(obj_id, obj_id, tid)

        for k, v in data.items():
            sk = make_sec_key(k, v)
            existing = self.storage.sec_index.search(sk)
            new_val = [obj_id] if existing is None else existing + [obj_id]
            self.storage.sec_index.insert(sk, new_val, tid)

        self.storage.txn.commit(tid)
        return obj_id

    # ✅ UPDATE
    def update(self, object_id, changes: dict):
        tid = self.storage.txn.begin()

        parent = self.vm.get_latest(object_id)

        fields = []

        for k, v in changes.items():
            key_chunk = self.storage.chunk.put(k.encode(), tid)
            val_chunk = self.storage.chunk.put(v, tid)
            fields.append((key_chunk, 1, val_chunk))

        new_obj_id = self.storage.obj.put(fields=fields, txn_id=tid)

        vid = self.vm.create_version(object_id, parent, new_obj_id)

        self._persist_version_meta(tid, vid, object_id, parent)
        self._persist_version_object(tid, vid, new_obj_id)

        for k, v in changes.items():
            sk = make_sec_key(k, v)
            existing = self.storage.sec_index.search(sk)
            new_val = [object_id] if existing is None else existing + [object_id]
            self.storage.sec_index.insert(sk, new_val, tid)

        self.storage.txn.commit(tid)
        return vid

    # ✅ persist version metadata
    def _persist_version_meta(self, tid, vid, object_id, parent):
        parent_val = b"None" if parent is None else str(parent).encode()
        ts = str(self.vm.version.get(vid)["timestamp"]).encode()

        fields = [
            (self.storage.chunk.put(b"kind", tid), 1, self.storage.chunk.put(b"version_meta", tid)),
            (self.storage.chunk.put(b"version_id", tid), 1, self.storage.chunk.put(str(vid).encode(), tid)),
            (self.storage.chunk.put(b"object_id", tid), 1, self.storage.chunk.put(str(object_id).encode(), tid)),
            (self.storage.chunk.put(b"parent", tid), 1, self.storage.chunk.put(parent_val, tid)),
            (self.storage.chunk.put(b"timestamp", tid), 1, self.storage.chunk.put(ts, tid)),
        ]

        self.storage.obj.put(fields=fields, txn_id=tid)

    # ✅ persist version → object mapping
    def _persist_version_object(self, tid, vid, obj_id):
        fields = [
            (self.storage.chunk.put(b"kind", tid), 1, self.storage.chunk.put(b"version_obj", tid)),
            (self.storage.chunk.put(b"version_id", tid), 1, self.storage.chunk.put(str(vid).encode(), tid)),
            (self.storage.chunk.put(b"object_ref", tid), 1, self.storage.chunk.put(str(obj_id).encode(), tid)),
        ]

        self.storage.obj.put(fields=fields, txn_id=tid)

    # ✅ rebuild versions from storage
    def _rebuild_versions(self):
        for obj_id in self.storage.obj.index.keys():
            obj = self.storage.obj.get(obj_id)

            data = {}

            for k, _, v in obj["fields"]:
                key = self.storage.chunk.get(k).decode()
                val = self.storage.chunk.get(v).decode()
                data[key] = val

            if data.get("kind") == "version_meta":
                vid = int(data["version_id"])
                oid = int(data["object_id"])
                parent = None if data["parent"] == "None" else int(data["parent"])
                ts = int(data["timestamp"])

                self.vm.version.versions[vid] = {
                    "node_id": oid,
                    "parent": parent,
                    "timestamp": ts,
                }

                self.vm.object_versions[oid] = vid

            elif data.get("kind") == "version_obj":
                vid = int(data["version_id"])
                oid = int(data["object_ref"])

                self.vm.version_objects[vid] = oid

    # ✅ GET
    def get(self, object_id):
        vid = self.vm.get_latest(object_id)
        return None if vid is None else self.vm.resolve(self.storage, object_id, vid)

    # ✅ FIND
    def find(self, field, value):
        key = make_sec_key(field, value)
        return self.storage.sec_index.search(key) or []

    # ✅ RANGE
    def range(self, start_id, end_id):
        return self.storage.index.range(start_id, end_id)

    # ✅ VERSION HISTORY
    def get_versions(self, object_id):
        return self.vm.get_versions(object_id)

    # ✅ TIME TRAVEL
    def get_as_of(self, object_id, timestamp):
        return self.vm.get_as_of(self.storage, object_id, timestamp)

    # ✅ TEMP: compaction disabled
    def compact(self):
        return
