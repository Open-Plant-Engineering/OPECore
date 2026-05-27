import tempfile
import os

from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.txn.manager import TransactionManager
from opecore.recovery.rebuilder import RecoveryManager


def test_full_recovery():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        # first run
        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)

            chunk = ChunkStore(fm)
            obj_store = ObjectStore(fm, chunk)

            tid = txn_mgr.begin()

            key = chunk.put(b"amount", tid)
            val = chunk.put(b"100", tid)

            obj_id = obj_store.put(fields=[(key, 1, val)], txn_id=tid)

            txn_mgr.commit(tid)

        # restart + rebuild
        with FileManager(path) as fm:
            chunk = ChunkStore(fm)
            obj_store = ObjectStore(fm, chunk)

            recovery = RecoveryManager(fm, chunk, obj_store)
            recovery.rebuild()

            obj = obj_store.get(obj_id)

            assert obj["object_id"] == obj_id
