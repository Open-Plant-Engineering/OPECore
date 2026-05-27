import tempfile
import os
from opecore.api.db import Database


def test_basic_versioning():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"a": b"1"})

        v1 = db.object_versions[oid]

        db.update(oid, {"a": b"2"})
        v2 = db.object_versions[oid]

        assert v2 != v1

        meta = db.version.get(v2)
        assert meta["parent"] == v1

        db.close()


