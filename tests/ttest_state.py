from opecore.state.state import StateEngine
import json


def make_record(data):
    return json.dumps(data).encode()


def test_set_and_get():
    s = StateEngine()

    s.apply(make_record({
        "op": "SET",
        "path": "/a",
        "value": {"x": 1}
    }))

    assert s.get("/a") == {"x": 1}


def test_delete():
    s = StateEngine()

    s.apply(make_record({
        "op": "SET",
        "path": "/a",
        "value": {"x": 1}
    }))

    s.apply(make_record({
        "op": "DELETE",
        "path": "/a"
    }))

    assert s.get("/a") is None


def test_rebuild():
    s = StateEngine()

    records = [
        make_record({"op": "SET", "path": "/a", "value": 1}),
        make_record({"op": "SET", "path": "/b", "value": 2}),
        make_record({"op": "DELETE", "path": "/a"})
    ]

    s.rebuild(records)

    assert s.get("/a") is None
    assert s.get("/b") == 2


def test_list_paths():
    s = StateEngine()

    s.apply(make_record({"op": "SET", "path": "/a", "value": 1}))
    s.apply(make_record({"op": "SET", "path": "/b", "value": 2}))

    paths = s.list_paths()

    assert "/a" in paths
    assert "/b" in paths