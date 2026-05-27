import tempfile
import os
from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.txn.manager import TransactionManager


def test_chunk_put_get():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            store = ChunkStore(fm)

            tid = txn_mgr.begin()

            cid = store.put(b"hello", tid)

            txn_mgr.commit(tid)

            data = store.get(cid)
            assert data == b"hello"


def test_chunk_dedup():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            store = ChunkStore(fm)

            tid = txn_mgr.begin()

            a = store.put(b"x", tid)
            b = store.put(b"x", tid)

            txn_mgr.commit(tid)

            assert a == b
