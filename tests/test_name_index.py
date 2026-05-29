from opecore.db.json_db import JsonDB
from opecore.model.node import Node
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex


def test_unique_name(tmp_path):

    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    n1 = Node(attributes={"name": "pipe1"})
    db.create_node(n1)

    n2 = Node(attributes={"name": "pipe1"})

    try:
        db.create_node(n2)
        assert False
    except ValueError:
        assert True

def test_lookup_by_name(tmp_path):
    from opecore.model.node import Node

    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    node = Node(attributes={"name": "zone1"})
    db.create_node(node)

    found = db.get_by_name("zone1")

    assert found.refno == node.refno

