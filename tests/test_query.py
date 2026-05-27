import tempfile
import os
from opecore.api.db import Database


def test_insert_get():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({
            "amount": b"100",
            "name": b"shivang"
        })

        result = db.get(oid)

        assert result["amount"] == b"100"
        assert result["name"] == b"shivang"

        db.close()


def test_find():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        db.insert({"amount": b"100"})
        db.insert({"amount": b"200"})
        db.insert({"amount": b"100"})

        res = db.find("amount", b"100")

        assert len(res) == 2

        db.close()