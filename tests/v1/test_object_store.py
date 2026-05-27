import tempfile
import os

from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.chunk_store import ChunkStore
from opecore.v1.storage.object_store import ObjectStore


class DummyID:
    def __init__(self):
        self.i = 1

    def generate(self):
        self.i += 1
        return self.i


def test_object_put_get():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)
        id_gen = DummyID()

        store = ObjectStore(fm, chunk, id_gen)

        key = chunk.put(b"k", 1)
        val = chunk.put(b"v", 1)

        obj_id = store.put(
            fields=[(key, 1, val)],
            txn_id=1
        )

        obj = store.get(obj_id)

        assert obj["object_id"] == obj_id
        assert len(obj["fields"]) == 1

        fm.close()


def test_object_not_found():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)
        id_gen = DummyID()

        store = ObjectStore(fm, chunk, id_gen)

        try:
            store.get(999)
        except KeyError:
            assert True
        else:
            assert False

        fm.close()