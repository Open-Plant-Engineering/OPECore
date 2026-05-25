def test_query_multiple(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    # Create sample data
    engine.update_object(1, {"type": "Device", "owner": 1}, "A")
    engine.update_object(2, {"type": "Device", "owner": 2}, "A")
    engine.update_object(3, {"type": "Site", "owner": 1}, "A")

    result = engine.query_multiple({
        "type": "Device",
        "owner": 1
    })

    assert 1 in result
    assert 2 not in result
    assert 3 not in result

def test_query_single(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")
    engine.update_object(2, {"type": "Site"}, "A")

    result = engine.query("type", "Device")

    assert 1 in result
    assert 2 not in result

def test_query_and_condition(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device", "owner": 1}, "A")
    engine.update_object(2, {"type": "Device", "owner": 2}, "A")
    engine.update_object(3, {"type": "Site", "owner": 1}, "A")

    result = engine.query_multiple({
        "type": "Device",
        "owner": 1
    })

    assert result == {1}

def test_query_no_match(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")

    result = engine.query_multiple({
        "type": "Site"
    })

    assert result == set()

def test_query_after_update(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")
    engine.update_object(1, {"type": "Site"}, "A")

    result = engine.query("type", "Site")

    assert 1 in result
    assert 1 not in engine.query("type", "Device")

import pytest


def test_query_single(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")
    engine.update_object(2, {"type": "Site"}, "A")

    result = engine.query("type", "Device")

    assert 1 in result
    assert 2 not in result


def test_query_and_condition(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device", "owner": 1}, "A")
    engine.update_object(2, {"type": "Device", "owner": 2}, "A")
    engine.update_object(3, {"type": "Site", "owner": 1}, "A")

    result = engine.query_multiple({
        "type": "Device",
        "owner": 1
    })

    assert result == {1}


def test_query_no_match(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")

    result = engine.query_multiple({
        "type": "Site"
    })

    assert result == set()


def test_query_after_update(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")
    engine.update_object(1, {"type": "Site"}, "A")

    result = engine.query("type", "Site")

    assert 1 in result
    assert 1 not in engine.query("type", "Device")


def test_query_or_condition(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")
    engine.update_object(2, {"type": "Site"}, "A")
    engine.update_object(3, {"type": "Other"}, "A")

    result = engine.query_or([
        {"type": "Device"},
        {"type": "Site"}
    ])

    assert result == {1, 2}


def test_query_complex(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device", "owner": 1}, "A")
    engine.update_object(2, {"type": "Site", "owner": 1}, "A")
    engine.update_object(3, {"type": "Device", "owner": 2}, "A")

    result = engine.query_complex({
        "AND": {"owner": 1},
        "OR": [
            {"type": "Device"},
            {"type": "Site"}
        ]
    })

    assert result == {1, 2}


def test_query_only_or(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device"}, "A")
    engine.update_object(2, {"type": "Site"}, "A")

    result = engine.query_complex({
        "OR": [
            {"type": "Device"},
            {"type": "Site"}
        ]
    })

    assert result == {1, 2}


def test_query_only_and(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"type": "Device", "owner": 1}, "A")
    engine.update_object(2, {"type": "Device", "owner": 2}, "A")

    result = engine.query_complex({
        "AND": {"type": "Device", "owner": 1}
    })

    assert result == {1}
