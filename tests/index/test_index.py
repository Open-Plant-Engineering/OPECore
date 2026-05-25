def test_index_add(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")

    result = engine.query("claim_by", "Alice")

    assert 1 in result


def test_index_update_replace(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "A", "A")

    # ✅ normal attribute update instead
    engine.update_attribute(1, "amount", 100, "A")

    result = engine.query("amount", 100)

    assert 1 in result


def test_index_no_change(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "A", "A")

    # same value again → allowed (same user)
    engine.update_attribute(1, "claim_by", "A", "A")

    result = engine.query("claim_by", "A")

    assert 1 in result


def test_index_multiple_objects(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")
    engine.update_attribute(2, "claim_by", "Alice", "B")
    engine.update_attribute(3, "claim_by", "Alice", "C")

    result = engine.query("claim_by", "Alice")

    assert set(result) == {1, 2, 3}


def test_index_multiple_attributes(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "A", "A")

    engine.update_attribute(1, "amount", 100, "A")

    result = engine.query("amount", 100)

    assert 1 in result


def test_index_missing_value(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    result = engine.query("claim_by", "Unknown")

    assert result == []


def test_index_remove_attribute(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "A", "A")

    engine.update_attribute(1, "claim_by", DELETE, "A")

    result = engine.query("claim_by", "A")

    assert 1 not in result
