def test_wal_prepare_commit(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})
    txn.commit()

    data = engine.read_latest(1)

    assert b"100" in data