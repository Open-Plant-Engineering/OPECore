from opecore.storage.log import AppendOnlyLog
from opecore.state.store import StateStore
import json


def test_store_integration(tmp_path):
    log = AppendOnlyLog(str(tmp_path / "data.log"))

    log.append(json.dumps({
        "op": "SET",
        "path": "/a",
        "value": 100
    }).encode())

    store = StateStore(log)
    store.load()

    assert store.get("/a") == 100