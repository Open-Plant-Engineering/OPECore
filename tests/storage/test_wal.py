def test_wal_recovery(tmp_path):
    from opecore.core.engine import Engine

    db_path = str(tmp_path / "test.db")

    # ✅ simulate crash BEFORE commit completes
    engine = Engine(db_path)

    # directly write WAL entry (simulate crash before commit finishes)
    engine.storage.wal.log_transaction(
        "A",
        {
            "1": {"claim_by": "Alice"}
        }
    )

    # ✅ new engine triggers recovery
    engine2 = Engine(db_path)

    data = engine2.read_latest(1)

    assert b"Alice" in data