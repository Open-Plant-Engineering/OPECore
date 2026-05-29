from opecore.query.query_engine import QueryEngine
from opecore.model.node import Node
from opecore.db.json_db import JsonDB
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex


def setup_db(tmp_path):
    cs = ChunkStore(str(tmp_path / "chunks.json"))
    ni = NameIndex(str(tmp_path / "index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))

    ts.create_type("ITEM", {
        "name": "string",
        "value": "real"
    })

    db = JsonDB(str(tmp_path / "db.json"), cs, ni, ts, gindex)
    return db


# ✅ test equality query
def test_filter(tmp_path):
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

    result = qe.filter({"name": "a"})

    assert len(result) == 1
    assert result[0].attributes["name"] == "a"

def test_single_filter(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({"name": "a"})

    assert len(result) == 1

def test_and_filter(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "name": "a",
        "value": 10
    })

    assert len(result) == 1
    assert result[0].attributes["value"] == 10

def test_no_match(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    db.create_node(n1)

    result = qe.filter({
        "name": "b"
    })

    assert len(result) == 0

def test_or_condition(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "or": [
            {"name": "a"},
            {"value": 20}
        ]
    })

    assert len(result) == 2

def test_or_no_match(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    db.create_node(n1)

    result = qe.filter({
        "or": [
            {"name": "x"},
            {"value": 999}
        ]
    })

    assert len(result) == 0

def test_and_or_mix(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})
    n3 = Node(attributes={"type": "ITEM", "name": "c", "value": 30})

    db.create_node(n1)
    db.create_node(n2)
    db.create_node(n3)

    result = qe.filter({
        "or": [
            {"and": [
                {"name": "a"},
                {"value": 10}
            ]},
            {"name": "b"}
        ]
    })

    assert len(result) == 2


def test_and_still_works(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "and": [
            {"name": "a"},
            {"value": 10}
        ]
    })

    assert len(result) == 1


def test_gt_operator(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "value": {"gt": 15}
    })

    assert len(result) == 1
    assert result[0].attributes["value"] == 20

def test_in_operator(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "name": {"in": ["a", "c"]}
    })

    assert len(result) == 1

def test_like_operator(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "pipe1", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "zone1", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "name": {"like": "pipe*"}
    })

    assert len(result) == 1

def test_range_operator(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "value": {"gte": 10, "lte": 20}
    })

    assert len(result) == 2

def test_index_lookup(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    db.create_node(n1)

    result = qe.filter({"name": "a"})

    assert len(result) == 1

def test_index_and_condition(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    db.create_node(n1)

    result = qe.filter({
        "and": [
            {"name": "a"},
            {"value": 10}
        ]
    })

    assert len(result) == 1

def test_index_no_match(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    result = qe.filter({"name": "missing"})

    assert len(result) == 0

def test_fallback_scan(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "value": {"gt": 10}
    })

    assert len(result) == 1

def test_generic_index(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 20})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({"value": 10})

    assert len(result) == 1

def test_and_with_index(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    n2 = Node(attributes={"type": "ITEM", "name": "b", "value": 10})

    db.create_node(n1)
    db.create_node(n2)

    result = qe.filter({
        "and": [
            {"value": 10},
            {"name": "a"}
        ]
    })

    assert len(result) == 1

def test_fallback_when_no_index(tmp_path):
    db = setup_db(tmp_path)
    qe = QueryEngine(db)

    n1 = Node(attributes={"type": "ITEM", "name": "a", "value": 10})
    db.create_node(n1)

    result = qe.filter({
        "value": {"gt": 5}
    })

    assert len(result) == 1

