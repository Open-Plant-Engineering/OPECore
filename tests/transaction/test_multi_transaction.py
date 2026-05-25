def test_multi_object_transaction(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    tx = engine.begin_transaction("A")

    tx.update(1, {"amount": 100})
    tx.update(2, {"claim_by": "Alice"})

    tx.commit()

    assert b"100" in engine.read_latest(1)
    assert b"Alice" in engine.read_latest(2)