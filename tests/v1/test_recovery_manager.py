import tempfile
import os

from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.chunk_store import ChunkStore
from opecore.v1.storage.object_store import ObjectStore
from opecore.v1.storage.txn_manager import TransactionManager
from opecore.v1.storage.recovery_manager import RecoveryManager
from opecore.v1.domain.id_generator import SnowflakeIDGenerator


def test_recovery_rebuilds_indexes():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)
        id_gen = SnowflakeIDGenerator()
        obj = ObjectStore(fm, chunk, id_gen)
        txn = TransactionManager(fm)

        # write data
        tid = txn.begin()

        k = chunk.put(b"k", tid)
        v = chunk.put(b"v", tid)

        obj_id = obj.put([(k, 1, v)], txn_id=tid)

        txn.commit(tid)

        # simulate restart (new objects)
        fm2 = FileManager(path)
        chunk2 = ChunkStore(fm2)
        obj2 = ObjectStore(fm2, chunk2, id_gen)

        recovery = RecoveryManager(fm2, chunk2, obj2)
        recovery.rebuild()

        # ✅ verify recovered indexes
        assert obj_id in obj2.index
        assert k in chunk2.index
        assert v in chunk2.index

        fm.close()
        fm2.close()