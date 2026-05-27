import tempfile, os

from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.txn.manager import TransactionManager
from opecore.recovery.rebuilder import RecoveryManager
from opecore.recovery.snapshot import SnapshotManager


def test_snapshot_fast_recovery():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            chunk = ChunkStore(fm)
            obj = ObjectStore(fm, chunk)
            snap = SnapshotManager(fm)

            tid = txn_mgr.begin()

            key = chunk.put(b"a", tid)
            val = chunk.put(b"1", tid)
            oid = obj.put(fields=[(key, 1, val)], txn_id=tid)

            txn_mgr.commit(tid)

            # save snapshot
            snap.save(tid, chunk, obj, last_offset=0)

        # restart
        with FileManager(path) as fm:
            chunk = ChunkStore(fm)
            obj = ObjectStore(fm, chunk)

            rec = RecoveryManager(fm, chunk, obj)
            rec.rebuild()

            assert obj.get(oid)["object_id"] == oid
