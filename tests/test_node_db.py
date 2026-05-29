from opecore.db.json_db import JsonDB
from opecore.model.node import Node
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex


def test_create_node(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    db = JsonDB(str(tmp_path / "main.db"), store, index)

    node = Node( attributes = { 
        "name":"zone1", 
        "node_type":"zone"
        } )
    ref = db.create_node(node)

    loaded = db.get_node(ref)

    assert loaded.attributes["name"] == "zone1"