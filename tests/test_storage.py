from opecore.storage.engine import StorageEngine


def test_append_and_read():
    db = StorageEngine("test.db")
    db.append(1, b"test")

    data = db.read_latest(1)
    assert data == b"test"
