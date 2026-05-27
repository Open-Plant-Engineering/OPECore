import tempfile
import os
import time
from opecore.api.db import Database


def test_time_travel():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({
            "name": b"P-1001",
        })

        t1 = int(time.time() * 1000)

        time.sleep(0.01)

        db.update(oid, {
            "name": b"P-2001"
        })

        old = db.get_as_of(oid, t1)
        latest = db.get(oid)

        assert old["name"] == b"P-1001"
        assert latest["name"] == b"P-2001"

        db.close()
