from opecore.storage.engine import StorageEngine


def test_append_and_read():
    db = StorageEngine("test.db")
    db.append(1, b"test")

    records = db.read_all()
    assert len(records) >= 1
