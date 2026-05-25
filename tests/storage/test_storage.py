import time


def test_append_and_read_latest(tmp_path):
    from opecore.storage.engine import StorageEngine

    db = StorageEngine(str(tmp_path / "test.db"))

    db.append(1, b"Alice")
    db.append(1, b"Bob")

    result = db.read_latest(1)

    assert result == b"Bob"


def test_version_chain_read_as_of(tmp_path):
    from opecore.storage.engine import StorageEngine

    db = StorageEngine(str(tmp_path / "test.db"))

    db.append(1, b"Alice")

    # ensure distinct timestamps
    time.sleep(0.001)
    t1 = time.time()

    time.sleep(0.001)
    db.append(1, b"Bob")

    time.sleep(0.001)
    t2 = time.time()

    time.sleep(0.001)
    db.append(1, b"Carol")

    # ✅ snapshot before Bob → should return Alice
    result1 = db.read_as_of(1, t1)
    assert result1 == b"Alice"

    # ✅ snapshot before Carol → should return Bob
    result2 = db.read_as_of(1, t2)
    assert result2 == b"Bob"

    # ✅ latest should be Carol
    latest = db.read_latest(1)
    assert latest == b"Carol"


def test_multiple_objects(tmp_path):
    from opecore.storage.engine import StorageEngine

    db = StorageEngine(str(tmp_path / "test.db"))

    db.append(1, b"Alice")
    db.append(2, b"Bob")

    assert db.read_latest(1) == b"Alice"
    assert db.read_latest(2) == b"Bob"


def test_empty_read(tmp_path):
    from opecore.storage.engine import StorageEngine

    db = StorageEngine(str(tmp_path / "test.db"))

    assert db.read_latest(1) is None
    assert db.read_as_of(1, time.time()) is None