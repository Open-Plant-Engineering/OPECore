import os
import tempfile

from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.index.btree import BTree
from opecore.txn.manager import TransactionManager
from opecore.recovery.rebuilder import RecoveryManager
from opecore.util.hash import make_sec_key


class Compactor:
    def __init__(self, db):
        self.db = db

    def compact(self):
        old_path = self.db.fm.path

        with tempfile.TemporaryDirectory() as tmp:
            new_path = os.path.join(tmp, "compacted.db")

            # ✅ WRITE NEW COMPACTED FILE
            with FileManager(new_path) as new_fm:
                txn = TransactionManager(new_fm)

                new_chunk = ChunkStore(new_fm)
                new_obj = ObjectStore(new_fm, new_chunk)
                new_index = BTree(new_fm)
                new_sec_index = BTree(new_fm)

                tid = txn.begin()

                # ✅ COPY LIVE OBJECTS
                for obj_id in self.db.obj.index.keys():
                    obj = self.db.obj.get(obj_id)

                    new_fields = []

                    for k, typ, v in obj["fields"]:
                        key_data = self.db.chunk.get(k)
                        val_data = self.db.chunk.get(v)

                        new_k = new_chunk.put(key_data, tid)
                        new_v = new_chunk.put(val_data, tid)

                        new_fields.append((new_k, typ, new_v))

                    new_obj_id = new_obj.put(
                        fields=new_fields,
                        txn_id=tid
                    )

                    # ✅ preserve original object_id mapping
                    new_obj.index[obj_id] = new_obj.index.pop(new_obj_id)

                    # ✅ PRIMARY INDEX
                    new_index.insert(obj_id, obj_id, tid)

                txn.commit(tid)

                # ✅ persist primary root (secondary rebuilt later)
                new_fm.update_root(new_index.root_offset)

            # ✅ CLOSE OLD DB BEFORE REPLACE
            self.db.close()

            self.db.chunk = None
            self.db.obj = None
            self.db.index = None
            self.db.sec_index = None
            self.db.fm = None

            # ✅ REPLACE FILE
            os.replace(new_path, old_path)

            # ✅ REOPEN CLEAN
            self.db.fm = FileManager(old_path)
            self.db.chunk = ChunkStore(self.db.fm)
            self.db.obj = ObjectStore(self.db.fm, self.db.chunk)
            self.db.index = BTree(self.db.fm)
            self.db.sec_index = BTree(self.db.fm)

            # ✅ REBUILD PRIMARY STATE
            RecoveryManager(
                self.db.fm,
                self.db.chunk,
                self.db.obj
            ).rebuild()

            # ✅ ✅ REBUILD SECONDARY INDEX (CRITICAL)
            for obj_id in self.db.obj.index.keys():
                obj = self.db.obj.get(obj_id)

                for k, _, v in obj["fields"]:
                    key_data = self.db.chunk.get(k)
                    val_data = self.db.chunk.get(v)

                    key_str = key_data.decode()

                    sk = make_sec_key(key_str, val_data)

                    existing = self.db.sec_index.search(sk)

                    if existing is None:
                        new_val = [obj_id]
                    else:
                        new_val = existing + [obj_id]

                    # ✅ txn_id=0 safe for rebuild
                    self.db.sec_index.insert(sk, new_val, txn_id=0)