import tempfile
import os
from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore


def test_object_roundtrip():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            chunk = ChunkStore(fm)
            store = ObjectStore(fm, chunk)

            key = chunk.put(b"amount")
            val = chunk.put(b"100")

            obj_id = store.put(fields=[(key, 1, val)])

            obj = store.get(obj_id)

            assert obj["object_id"] == obj_id
            assert len(obj["fields"]) == 1
