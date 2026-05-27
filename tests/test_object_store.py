import tempfile
import os
from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.txn.manager import TransactionManager


def test_object_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            chunk = ChunkStore(fm)
            store = ObjectStore(fm, chunk)

            tid = txn_mgr.begin()

            key = chunk.put(b"amount", tid)
            val = chunk.put(b"100", tid)

            obj_id = store.put(fields=[(key, 1, val)], txn_id=tid)

            txn_mgr.commit(tid)

            obj = store.get(obj_id)

            assert obj["object_id"] == obj_id
            assert len(obj["fields"]) == 1
