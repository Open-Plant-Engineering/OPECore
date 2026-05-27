import tempfile, os
from opecore.api.db import Database


def test_range_query():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        ids = []
        for i in range(10):
            oid = db.insert({"value": str(i).encode()})
            ids.append(oid)

        # take middle range
        res = db.range(ids[3], ids[6])

        assert len(res) >= 3

        db.close()
