from opecore.db.json_db import JsonDB
from opecore.model.node import Node
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex

def test_node_uses_chunk_store(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    db = JsonDB(str(tmp_path / "main.db"), store, index)

    node = Node(attributes={
        "name": "pipe1",
        "value": 100
    })

    db.create_node(node)

    # raw DB data
    raw = db.load()

    stored_node = list(raw["nodes"].values())[0]

    # should NOT store raw values
    assert stored_node["name"] != "pipe1"
    assert stored_node["value"] != 100

    # should store chunk IDs
    assert isinstance(stored_node["name"], str)
    assert isinstance(stored_node["value"], str)

    # verify resolution works
    loaded = db.get_node(node.refno)

    assert loaded.attributes["name"] == "pipe1"
    assert loaded.attributes["value"] == 100
