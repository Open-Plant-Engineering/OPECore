import tempfile
import os

from opecore.v1.api.database import Database


def test_secondary_index_basic():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid1 = db.insert({"name": b"A"})
        oid2 = db.insert({"name": b"B"})
        oid3 = db.insert({"name": b"A"})

        res = db.find("name", b"A")

        assert oid1 in res
        assert oid3 in res
        assert oid2 not in res

        db.close()


def test_secondary_index_after_update():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"name": b"A"})

        db.update(oid, {"name": b"B"})

        res_old = db.find("name", b"A")
        res_new = db.find("name", b"B")

        assert oid in res_old   # still exists historically
        assert oid in res_new

        db.close()
