from opecore.state.state import StateEngine
import json


def rec(x):
    return json.dumps(x).encode()


def build_state():
    s = StateEngine()

    s.apply(rec({"op": "SET", "path": "/a", "value": 1}))
    s.apply(rec({"op": "SET", "path": "/a/b", "value": 2}))
    s.apply(rec({"op": "SET", "path": "/a/b/c", "value": 3}))
    s.apply(rec({"op": "SET", "path": "/a/x", "value": 4}))

    return s


def test_exists():
    s = build_state()

    assert s.exists("/a") is True
    assert s.exists("/nope") is False


def test_list_children():
    s = build_state()

    children = s.list_children("/a")

    assert "/a/b" in children
    assert "/a/x" in children
    assert "/a/b/c" not in children  # not direct child


def test_list_subtree():
    s = build_state()

    subtree = s.list_subtree("/a")

    assert "/a" in subtree
    assert "/a/b" in subtree
    assert "/a/b/c" in subtree
    assert "/a/x" in subtree


def test_delete_affects_queries():
    s = build_state()

    s.apply(rec({"op": "DELETE", "path": "/a/b"}))

    assert s.exists("/a/b") is False

    children = s.list_children("/a")
    assert "/a/b" not in children
