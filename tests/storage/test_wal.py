def test_wal_recovery(tmp_path):
    from opecore.storage.engine import StorageEngine

    db_path = str(tmp_path / "test.db")

    # simulate crash BEFORE commit
    engine = StorageEngine(db_path)

    engine.wal.log(1, b'{"claim_by":"Alice"}')

    # new engine → recovery
    engine2 = StorageEngine(db_path)

    data = engine2.read_latest(1)

    assert b"Alice" in data