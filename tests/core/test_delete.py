def test_attribute_delete(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(
        1,
        {
            "claim_by": "Alice",
            "amount": 1000,
        },
        "A"
    )

    engine.update_object(
        1,
        {
            "claim_by": DELETE
        },
        "A"
    )

    data = engine.read_latest(1)

    assert b"claim_by" not in data
    assert b"1000" in data

    # index check
    assert 1 not in engine.query("claim_by", "Alice")