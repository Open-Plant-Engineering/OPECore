import tempfile
import os
from opecore.api.db import Database


def test_basic_versioning():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"a": b"1"})

        versions = db.get_versions(oid)
        v1 = versions[-1]

        db.update(oid, {"a": b"2"})
        db.update(oid, {"a": b"3"})

        versions = db.get_versions(oid)

        assert len(versions) == 3
        assert versions[0] != versions[1] != versions[2]

        data = db.get(oid)
        assert data["a"] == b"3"

        # ✅ CRITICAL FIX
        db.close()