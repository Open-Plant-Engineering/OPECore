import tempfile
import os
from opecore.api.db import Database


def test_update_creates_new_version():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({
            "name": b"P-1001",
            "type": b"PIPE"
        })

        db.update(oid, {
            "name": b"P-2001"
        })

        data = db.get(oid)

        assert data["name"] == b"P-2001"
        assert data["type"] == b"PIPE"  # inherited

        versions = db.get_versions(oid)

        assert len(versions) == 2

        db.close()
