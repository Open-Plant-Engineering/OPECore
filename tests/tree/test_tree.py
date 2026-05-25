def setup_tree(engine):
    # Root
    engine.update_object(1, {"name": "root", "owner": None}, "A")

    # Level 1
    engine.update_object(2, {"name": "child1", "owner": 1}, "A")
    engine.update_object(3, {"name": "child2", "owner": 1}, "A")

    # Level 2
    engine.update_object(4, {"name": "subchild1", "owner": 2}, "A")
    engine.update_object(5, {"name": "subchild2", "owner": 2}, "A")

def test_get_parent(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    assert engine.get_parent(2) == 1
    assert engine.get_parent(1) is None


def test_get_children(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    children = engine.get_children(1)

    assert set(children) == {2, 3}

def test_get_ancestors(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    ancestors = engine.get_ancestors(5)

    assert ancestors == [2, 1]

def test_get_subtree(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    subtree = engine.get_subtree(2)

    assert subtree == {2, 4, 5}

def test_subtree_root(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    subtree = engine.get_subtree(1)

    assert subtree == {1, 2, 3, 4, 5}

def test_query_in_subtree_basic(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    # add types
    engine.update_object(2, {"type": "Device"}, "A")
    engine.update_object(3, {"type": "Site"}, "A")
    engine.update_object(4, {"type": "Device"}, "A")

    result = engine.query_in_subtree(1, {"type": "Device"})

    assert result == {2, 4}

def test_query_in_subtree_scope(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    engine.update_object(3, {"type": "Device"}, "A")
    engine.update_object(4, {"type": "Device"}, "A")

    # subtree of node 2 only includes 2,4,5
    result = engine.query_in_subtree(2, {"type": "Device"})

    assert result == {4}

def test_query_in_subtree_no_match(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    result = engine.query_in_subtree(1, {"type": "Unknown"})

    assert result == set()


def test_query_complex_in_subtree_basic(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    # assign attributes
    engine.update_object(2, {"type": "Device", "status": "active"}, "A")
    engine.update_object(3, {"type": "Site", "status": "active"}, "A")
    engine.update_object(4, {"type": "Device", "status": "inactive"}, "A")
    engine.update_object(5, {"type": "Device", "status": "active"}, "A")

    result = engine.query_complex_in_subtree(1, {
        "AND": {"status": "active"},
        "OR": [
            {"type": "Device"},
            {"type": "Site"}
        ]
    })

    # Only active Device or Site under subtree(1)
    assert result == {2, 3, 5}

def test_query_complex_in_subtree_scope(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    engine.update_object(2, {"type": "Device"}, "A")
    engine.update_object(3, {"type": "Device"}, "A")
    engine.update_object(4, {"type": "Device"}, "A")

    result = engine.query_complex_in_subtree(2, {
        "OR": [
            {"type": "Device"}
        ]
    })

    # subtree(2) = {2,4,5}; among these → only 2 and 4 match
    assert result == {2, 4}

def test_query_complex_in_subtree_only_and(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    engine.update_object(2, {"type": "Device", "owner": 1}, "A")
    engine.update_object(3, {"type": "Device", "owner": 1}, "A")
    engine.update_object(4, {"type": "Device", "owner": 2}, "A")

    result = engine.query_complex_in_subtree(1, {
        "AND": {"type": "Device", "owner": 1}
    })

    assert result == {2, 3}

def test_query_complex_in_subtree_only_or(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    engine.update_object(2, {"type": "Device"}, "A")
    engine.update_object(3, {"type": "Site"}, "A")
    engine.update_object(4, {"type": "Other"}, "A")

    result = engine.query_complex_in_subtree(1, {
        "OR": [
            {"type": "Device"},
            {"type": "Site"}
        ]
    })

    assert result == {2, 3}

def test_query_complex_in_subtree_no_match(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    result = engine.query_complex_in_subtree(1, {
        "AND": {"type": "Unknown"}
    })

    assert result == set()

def test_query_complex_in_deep_subtree(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))
    setup_tree(engine)

    engine.update_object(4, {"type": "Device", "status": "active"}, "A")
    engine.update_object(5, {"type": "Device", "status": "inactive"}, "A")

    result = engine.query_complex_in_subtree(2, {
        "AND": {"type": "Device"},
        "OR": [{"status": "active"}]
    })

    # subtree(2) = {2,4,5}
    # only object 4 matches
    assert result == {4}

