from opecore.storage.log import AppendOnlyLog
from opecore.state.store import StateStore
import json


def test_store_query(tmp_path):
    log = AppendOnlyLog(str(tmp_path / "data.log"))

    log.append(json.dumps({"op": "SET", "path": "/a", "value": 1}).encode())
    log.append(json.dumps({"op": "SET", "path": "/a/b", "value": 2}).encode())
    log.append(json.dumps({"op": "SET", "path": "/a/c", "value": 3}).encode())

    store = StateStore(log)
    store.load()

    children = store.list_children("/a")

    assert "/a/b" in children
    assert "/a/c" in children
