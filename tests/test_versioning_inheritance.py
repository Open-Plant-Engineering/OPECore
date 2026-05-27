import tempfile
import os
from opecore.api.db import Database


def test_version_inheritance():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({
            "name": b"P-1001",
            "type": b"PIPE",
            "zone": b"ZONE-A"
        })

        db.update(oid, {
            "name": b"P-2001"
        })

        db.update(oid, {
            "zone": b"ZONE-B"
        })

        data = db.get(oid)

        assert data["name"] == b"P-2001"
        assert data["type"] == b"PIPE"
        assert data["zone"] == b"ZONE-B"

        db.close()
