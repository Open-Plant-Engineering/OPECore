from opecore.query.query_engine import QueryEngine
from opecore.model.node import Node
from opecore.db.json_db import JsonDB
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore


def setup_db(tmp_path):
    cs = ChunkStore(str(tmp_path / "chunks.json"))
    ni = NameIndex(str(tmp_path / "index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))

    ts.create_type("ITEM", {
        "name": "string",
        "value": "real"
    })

    db = JsonDB(str(tmp_path / "db.json"), cs, ni, ts)
    return db


# ✅ test equality query
def test_filter_equal(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={
        "type": "ITEM",
        "name": "a",
        "value": 10
    })

    n2 = Node(attributes={
        "type": "ITEM",
        "name": "b",
        "value": 20
    })

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter_equal("name", "a")

    assert len(result) == 1
    assert result[0].attributes["name"] == "a"