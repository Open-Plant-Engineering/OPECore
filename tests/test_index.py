from opecore.core.engine import Engine


def test_index_query(tmp_path):
    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "userA")
    engine.update_attribute(2, "claim_by", "Bob", "userB")
    engine.update_attribute(3, "claim_by", "Alice", "userC")

    result = engine.index.query("claim_by", "Alice")

    assert 1 in result
    assert 3 in result
    assert 2 not in result
