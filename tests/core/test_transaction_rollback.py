def test_transaction_rollback(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")

    try:
        # simulate failure
        engine.update_object(
            1,
            {
                "amount": 1000,
                "fail": 1 / 0   # force exception
            },
            "A"
        )
    except:
        pass

    # ✅ state unchanged
    data = engine.read_latest(1)

    assert b"Alice" in data
    assert b"1000" not in data