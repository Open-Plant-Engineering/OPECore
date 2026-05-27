import os
import tempfile

from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.chunk_store import ChunkStore
from opecore.v1.storage.object_store import ObjectStore
from opecore.v1.storage.btree import BTree
from opecore.v1.storage.txn_manager import TransactionManager

from opecore.v1.domain.id_generator import SnowflakeIDGenerator


class CompactionManager:
    """
    SOLID v1 CompactionManager

    Responsibility:
    - Rebuild database into compact form
    - Copy only latest versions
    """

    def __init__(self, db):
        self.db = db

    # ------------------------
    # ENTRY POINT
    # ------------------------

    def compact(self):
        old_path = self.db.fm.path

        with tempfile.TemporaryDirectory() as tmp:
            new_path = os.path.join(tmp, "compacted.db")

            # ✅ create fresh storage stack
            fm = FileManager(new_path)
            chunk = ChunkStore(fm)
            id_gen = SnowflakeIDGenerator()
            obj = ObjectStore(fm, chunk, id_gen)
            index = BTree(fm)
            txn = TransactionManager(fm)

            tid = txn.begin()

            version_records = []

            for object_id in list(self.db.vm.object_versions.keys()):
                vid = self.db.vm.latest(object_id)
                phys_id = self.db.vm.version_objects.get(vid)

                if phys_id is None:
                    continue

                obj_data = self.db.obj.get(phys_id)

                new_fields = []

                for k, typ, v in obj_data["fields"]:
                    new_k = chunk.put(self.db.chunk.get(k), tid)
                    new_v = chunk.put(self.db.chunk.get(v), tid)
                    new_fields.append((new_k, typ, new_v))

                new_phys_id = obj.put(new_fields, txn_id=tid)

                parent = self.db.vm.parents.get(vid)

                version_records.append((vid, object_id, parent, new_phys_id))

                index.insert(object_id, object_id, tid)

            for vid, oid, parent, phys in version_records:
                def put_pair(k, v):
                    kc = chunk.put(k.encode(), tid)
                    vc = chunk.put(v.encode(), tid)
                    return (kc, 1, vc)

                fields = [
                    put_pair("kind", "version"),
                    put_pair("vid", str(vid)),
                    put_pair("oid", str(oid)),
                    put_pair("parent", "None" if parent is None else str(parent)),
                    put_pair("phys", str(phys))
                ]

                obj.put(fields, txn_id=tid)

            txn.commit(tid)

            # ✅ update root pointer
            if index.root_offset:
                fm.update_root(index.root_offset)

            # ✅ close new file
            fm.close()

            # ✅ close old DB BEFORE replace
            self.db.close()

            # ✅ replace file atomically
            os.replace(new_path, old_path)

        # ✅ reopen DB cleanly
        self.db.fm.close()
        self.db.__dict__.clear()
        self.db.__init__(old_path)
