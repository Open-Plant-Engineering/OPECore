from opecore.db.json_db import JsonDB
from opecore.model.node import Node


def test_create_node(tmp_path):
    db = JsonDB(str(tmp_path / "main.db"))

    node = Node( attributes = { 
        "name":"zone1", 
        "node_type":"zone"
        } )
    ref = db.create_node(node)

    loaded = db.get_node(ref)

    assert loaded.attributes["name"] == "zone1"