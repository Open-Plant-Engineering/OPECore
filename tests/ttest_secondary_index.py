import tempfile
import os
from opecore.api.db import Database


def test_secondary_index():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        a = db.insert({"amount": b"100"})
        b = db.insert({"amount": b"200"})
        c = db.insert({"amount": b"100"})

        res = db.find("amount", b"100")

        assert a in res
        assert c in res
        assert b not in res

        db.close()
