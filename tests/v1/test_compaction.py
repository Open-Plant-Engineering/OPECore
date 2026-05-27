import tempfile
import os

from opecore.v1.api.database import Database
from opecore.v1.storage.compaction_manager import CompactionManager


def test_compaction_reduces_size():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"a": b"1"})

        for i in range(5):
            db.update(oid, {"a": str(i).encode()})

        size_before = os.path.getsize(path)

        compactor = CompactionManager(db)
        compactor.compact()

        size_after = os.path.getsize(path)

        # ✅ should shrink
        assert size_after <= size_before

        data = db.get(oid)
        assert data["a"] == b"4"

        db.close()
