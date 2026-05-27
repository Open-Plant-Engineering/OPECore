import tempfile
import os
from opecore.api.db import Database


def test_basic_versioning():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        # create object
        oid = db.insert({
            "name": b"P-1001",
            "type": b"PIPE"
        })

        data = db.get(oid)

        assert data["name"] == b"P-1001"
        assert data["type"] == b"PIPE"

        versions = db.get_versions(oid)

        assert len(versions) == 1

        db.close()
