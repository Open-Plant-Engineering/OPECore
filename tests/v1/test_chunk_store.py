import tempfile
import os

from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.chunk_store import ChunkStore


def test_put_and_get_chunk():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)

        data = b"hello"

        cid = chunk.put(data, txn_id=1)
        result = chunk.get(cid)

        assert result == data

        fm.close()


def test_deduplication():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)

        data = b"same-data"

        cid1 = chunk.put(data, txn_id=1)
        cid2 = chunk.put(data, txn_id=2)

        assert cid1 == cid2

        fm.close()


def test_missing_chunk():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)

        try:
            chunk.get(b"invalid")
        except KeyError:
            assert True
        else:
            assert False

        fm.close()