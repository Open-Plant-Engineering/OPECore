import tempfile
import os

from opecore.v1.api.database import Database


def test_snapshot_recovery():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"a": b"1"})

        db.close()

        # reopen should use snapshot
        db2 = Database(path)

        data = db2.get(oid)

        assert data["a"] == b"1"

        db2.close()
