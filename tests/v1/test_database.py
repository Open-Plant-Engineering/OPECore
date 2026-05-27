import tempfile
import os

from opecore.v1.api.database import Database


def test_insert_and_get():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({
            "name": b"A",
            "type": b"PIPE"
        })

        data = db.get(oid)

        assert data["name"] == b"A"
        assert data["type"] == b"PIPE"

        db.close()


def test_update():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"name": b"A"})
        db.update(oid, {"name": b"B"})

        data = db.get(oid)

        assert data["name"] == b"B"

        db.close()


def test_version_history():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        oid = db.insert({"a": b"1"})
        db.update(oid, {"a": b"2"})
        db.update(oid, {"a": b"3"})

        versions = db.get_versions(oid)

        assert len(versions) == 3

        db.close()
