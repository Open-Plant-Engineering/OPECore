import tempfile
import os

from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.chunk_store import ChunkStore
from opecore.v1.storage.object_store import ObjectStore
from opecore.v1.domain.id_generator import SnowflakeIDGenerator
from opecore.v1.domain.version_manager import VersionManager


def test_version_chain_resolution():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        chunk = ChunkStore(fm)
        id_gen = SnowflakeIDGenerator()
        obj = ObjectStore(fm, chunk, id_gen)

        vm = VersionManager()

        # create base object
        k1 = chunk.put(b"name", 1)
        v1 = chunk.put(b"A", 1)

        o1 = obj.put([(k1, 1, v1)], txn_id=1)
        vid1 = vm.create(o1, None, o1)

        # update object
        v2 = chunk.put(b"B", 1)
        o2 = obj.put([(k1, 1, v2)], txn_id=1)

        vid2 = vm.create(o1, vid1, o2)

        result = vm.resolve(
            storage=type("S", (), {"obj": obj, "chunk": chunk}),
            object_id=o1,
            version_id=vid2
        )

        assert result["name"] == b"B"

        fm.close()


def test_version_history():
    vm = VersionManager()

    oid = 100

    v1 = vm.create(oid, None, 1)
    v2 = vm.create(oid, v1, 2)
    v3 = vm.create(oid, v2, 3)

    history = vm.history(oid)

    assert history == [v3, v2, v1]
