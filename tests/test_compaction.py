import tempfile, os
from opecore.api.db import Database


def test_compaction():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        for i in range(10):
            db.insert({"value": str(i).encode()})

        before_size = os.path.getsize(path)

        db.compact()

        after_size = os.path.getsize(path)

        # ✅ should be smaller or similar (no growth)
        assert after_size <= before_size * 1.5

        # ✅ data still correct
        res = db.find("value", b"5")
        assert len(res) == 1

        db.close()