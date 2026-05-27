from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.index.btree import BTree
from opecore.txn.manager import TransactionManager
from opecore.recovery.rebuilder import RecoveryManager


class Database:
    def __init__(self, path):
        self.fm = FileManager(path)
        self.txn = TransactionManager(self.fm)

        self.chunk = ChunkStore(self.fm)
        self.obj = ObjectStore(self.fm, self.chunk)
        self.index = BTree(self.fm)

        # ✅ rebuild state
        RecoveryManager(self.fm, self.chunk, self.obj).rebuild()

    def close(self):
        self.fm.close()

    # ✅ INSERT OBJECT
    def insert(self, data: dict):
        tid = self.txn.begin()

        fields = []

        for k, v in data.items():
            key_chunk = self.chunk.put(k.encode(), tid)
            val_chunk = self.chunk.put(v, tid)

            fields.append((key_chunk, 1, val_chunk))

        obj_id = self.obj.put(fields=fields, txn_id=tid)

        # ✅ primary index (object_id → object_id)
        self.index.insert(obj_id, obj_id, tid)

        self.txn.commit(tid)

        return obj_id

    # ✅ GET OBJECT
    def get(self, object_id):
        obj = self.obj.get(object_id)

        result = {}

        for k, _, v in obj["fields"]:
            key = self.chunk.get(k).decode()
            val = self.chunk.get(v)

            result[key] = val

        return result

    # ✅ SCAN (sequential)
    def scan(self):
        results = []

        for obj_id in self.obj.index.keys():
            results.append((obj_id, self.get(obj_id)))

        return results

    # ✅ SIMPLE FILTER (no secondary index yet)
    def find(self, field, value):
        results = []

        for obj_id in self.obj.index.keys():
            obj = self.obj.get(obj_id)

            for k, _, v in obj["fields"]:
                key = self.chunk.get(k).decode()
                val = self.chunk.get(v)

                if key == field and val == value:
                    results.append(obj_id)

        return results
