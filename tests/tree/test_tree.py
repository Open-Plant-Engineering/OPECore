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

