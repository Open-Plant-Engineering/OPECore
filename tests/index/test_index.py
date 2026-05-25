def test_index_add(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")

    result = engine.query("claim_by", "Alice")

    assert 1 in result


def test_index_update_replace(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")
    engine.update_attribute(1, "claim_by", "Bob", "A")

    # ✅ old value removed
    assert 1 not in engine.query("claim_by", "Alice")

    # ✅ new value added
    assert 1 in engine.query("claim_by", "Bob")


def test_index_no_change(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")
    engine.update_attribute(1, "claim_by", "Alice", "A")

    result = engine.query("claim_by", "Alice")

    # ✅ should not duplicate or lose
    assert 1 in result
    assert len(result) == 1


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

    engine.update_attribute(1, "claim_by", "Alice", "A")
    engine.update_attribute(1, "amount", 100, "A")

    claim_result = engine.query("claim_by", "Alice")
    amount_result = engine.query("amount", 100)

    assert 1 in claim_result
    assert 1 in amount_result


def test_index_missing_value(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    result = engine.query("claim_by", "Unknown")

    assert result == []


def test_index_remove_attribute(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    # initial
    engine.update_attribute(1, "claim_by", "Alice", "A")

    # simulate removal by overwriting entire object
    engine.update_attribute(1, "claim_by", None, "A")

    result = engine.query("claim_by", "Alice")

    assert 1 not in result
