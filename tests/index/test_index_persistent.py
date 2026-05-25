def test_index_persistence(tmp_path):
    from opecore.core.engine import Engine

    db_path = str(tmp_path / "test.db")

    engine = Engine(db_path)

    engine.update_attribute(1, "claim_by", "Alice", "A")
    engine.update_attribute(2, "claim_by", "Bob", "B")

    # simulate restart
    engine2 = Engine(db_path)

    result = engine2.query("claim_by", "Alice")

    assert 1 in result
    assert 2 not in result