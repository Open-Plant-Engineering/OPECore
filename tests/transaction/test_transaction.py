def test_multi_field_update(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(
        1,
        {
            "claim_by": "Alice",
            "amount": 1000,
        },
        "A"
    )

    data = engine.read_latest(1)

    assert b"Alice" in data
    assert b"1000" in data

def test_atomic_single_version(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(
        1,
        {
            "claim_by": "Alice",
            "amount": 1000,
        },
        "A"
    )

    records = engine.storage.read_all()

    # ✅ only ONE version should exist
    assert len(records) == 1

def test_update_existing_object(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")

    engine.update_object(
        1,
        {
            "amount": 2000,
        },
        "A"
    )

    data = engine.read_latest(1)

    assert b"Alice" in data
    assert b"2000" in data

def test_transaction_index(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(
        1,
        {
            "claim_by": "Alice",
            "amount": 1000,
        },
        "A"
    )

    assert 1 in engine.query("claim_by", "Alice")
    assert 1 in engine.query("amount", 1000)

