import tempfile
import os
from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore


def test_chunk_put_get():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            store = ChunkStore(fm)

            cid = store.put(b"hello")
            data = store.get(cid)

            assert data == b"hello"


def test_chunk_dedup():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            store = ChunkStore(fm)

            a = store.put(b"x")
            b = store.put(b"x")

            assert a == b