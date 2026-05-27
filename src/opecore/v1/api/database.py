from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.chunk_store import ChunkStore
from opecore.v1.storage.object_store import ObjectStore
from opecore.v1.storage.txn_manager import TransactionManager
from opecore.v1.storage.recovery_manager import RecoveryManager
from opecore.v1.storage.btree import BTree
from opecore.v1.storage.secondary_index import SecondaryIndex

from opecore.v1.domain.id_generator import SnowflakeIDGenerator
from opecore.v1.domain.version_manager import VersionManager


class Database:
    """
    SOLID v1 Database API

    Responsibility:
    - Orchestrate all components
    - Expose public operations
    """

    def __init__(self, path: str):
        # ✅ infra
        self.fm = FileManager(path)

        # ✅ storage
        self.chunk = ChunkStore(self.fm)
        self.id_gen = SnowflakeIDGenerator()
        self.obj = ObjectStore(self.fm, self.chunk, self.id_gen)
        self.txn = TransactionManager(self.fm)
        self.index = BTree(self.fm)

        # ✅ domain
        self.vm = VersionManager()
        self.sec_index = SecondaryIndex(BTree(self.fm))

        # ✅ recovery
        self._recover()

    # ------------------------
    # LIFECYCLE
    # ------------------------

    def close(self):
        self.fm.close()

    # ------------------------
    # RECOVERY
    # ------------------------

    def _recover(self):
        RecoveryManager(self.fm, self.chunk, self.obj).rebuild()
        self._rebuild_versions()

    # ------------------------
    # INSERT
    # ------------------------

    def insert(self, data: dict):
        tid = self.txn.begin()

        fields = []

        for k, v in data.items():
            k_chunk = self.chunk.put(k.encode(), tid)
            v_chunk = self.chunk.put(v, tid)
            fields.append((k_chunk, 1, v_chunk))

        # ✅ FIRST create object
        obj_id = self.obj.put(fields, txn_id=tid)

        # ✅ version
        vid = self.vm.create(obj_id, None, obj_id)
        self._persist_version(tid, vid, obj_id, None, obj_id)

        # ✅ NOW safe to index
        for k, v in data.items():
            self.sec_index.add(k, v, obj_id, tid)

        self.index.insert(obj_id, obj_id, tid)

        self.txn.commit(tid)

        return obj_id

    # ------------------------
    # UPDATE
    # ------------------------

    def update(self, object_id, changes: dict):
        tid = self.txn.begin()

        parent = self.vm.latest(object_id)

        fields = []

        for k, v in changes.items():
            k_chunk = self.chunk.put(k.encode(), tid)
            v_chunk = self.chunk.put(v, tid)
            fields.append((k_chunk, 1, v_chunk))

        new_obj = self.obj.put(fields, txn_id=tid)

        vid = self.vm.create(object_id, parent, new_obj)
        self._persist_version(tid, vid, object_id, parent, new_obj)

        for k, v in changes.items():
            self.sec_index.add(k, v, object_id, tid)

        self.txn.commit(tid)

        return vid

    # ------------------------
    # GET
    # ------------------------

    def get(self, object_id):
        vid = self.vm.latest(object_id)

        if vid is None:
            return None

        return self.vm.resolve(self._storage_view(), object_id, vid)

    # ------------------------
    # RANGE
    # ------------------------

    def range(self, start_id, end_id):
        return self.index.range(start_id, end_id)

    # ------------------------
    # VERSION HISTORY
    # ------------------------

    def get_versions(self, object_id):
        return self.vm.history(object_id)

    # ------------------------
    # INTERNAL
    # ------------------------

    def _storage_view(self):
        """
        Provide a minimal interface to VersionManager
        """
        return type(
            "StorageView",
            (),
            {
                "obj": self.obj,
                "chunk": self.chunk
            }
        )
    
    def _persist_version(self, tid, vid, object_id, parent, phys_id):
        def put_pair(k, v):
            kc = self.chunk.put(k.encode(), tid)
            vc = self.chunk.put(v.encode(), tid)
            return (kc, 1, vc)

        fields = [
            put_pair("kind", "version"),
            put_pair("vid", str(vid)),
            put_pair("oid", str(object_id)),
            put_pair("parent", "None" if parent is None else str(parent)),
            put_pair("phys", str(phys_id))
        ]

        self.obj.put(fields, txn_id=tid)

    def _rebuild_versions(self):
        self.vm.object_versions.clear()
        self.vm.version_objects.clear()
        self.vm.parents.clear()
    
        for obj_id in self.obj.index.keys():
            obj = self.obj.get(obj_id)
    
            data = {}
    
            for k, _, v in obj["fields"]:
                key = self.chunk.get(k).decode()
                val = self.chunk.get(v).decode()
                data[key] = val
    
            if data.get("kind") == "version":
                vid = int(data["vid"])
                oid = int(data["oid"])
                parent = None if data["parent"] == "None" else int(data["parent"])
                phys = int(data["phys"])
    
                self.vm.parents[vid] = parent
                self.vm.version_objects[vid] = phys
                self.vm.object_versions[oid] = vid

    def find(self, field, value):
        return self.sec_index.find(field, value)
    