def test_wal_transaction_recovery(tmp_path):
    from opecore.core.engine import Engine

    db_path = str(tmp_path / "test.db")

    engine = Engine(db_path)

    tx = engine.begin_transaction("A")
    tx.update(1, {"amount": 100})
    tx.update(2, {"claim_by": "Alice"})

    # simulate crash BEFORE commit finishes
    engine.storage.wal.log_transaction("A", {
        "1": {"amount": 100},
        "2": {"claim_by": "Alice"}
    })

    # new engine → recovery
    engine2 = Engine(db_path)

    assert b"100" in engine2.read_latest(1)
    assert b"Alice" in engine2.read_latest(2)

def test_wal_transaction_recovery_multi(tmp_path):
    from opecore.core.engine import Engine

    db_path = str(tmp_path / "test.db")

    engine = Engine(db_path)

    engine.storage.wal.log_transaction(
        "A",
        {
            "1": {"amount": 100},
            "2": {"claim_by": "Alice"}
        }
    )

    engine2 = Engine(db_path)

    assert b"100" in engine2.read_latest(1)
    assert b"Alice" in engine2.read_latest(2)