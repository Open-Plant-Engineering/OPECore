from opecore.model.node import Node
from opecore.db.json_db import DBEngine
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex

def test_create_type(tmp_path):
    ts = TypeStore(str(tmp_path / "types.json"))

    ts.create_type("PIPE", {
        "name": "string",
        "diameter": "real"
    })

    assert ts.exists("PIPE")

def test_valid_node(tmp_path):
    cs = ChunkStore(str(tmp_path / "chunks.json"))
    ni = NameIndex(str(tmp_path / "index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))

    ts.create_type("PIPE", {
        "name": "string",
        "diameter": "real"
    })

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = DBEngine(str(tmp_path / "db.json"), cs, ni, ts, gindex)

    node = Node(attributes={
        "type": "PIPE",
        "name": "P1",
        "diameter": 10.5
    })

    db.create_node(node)  # ✅ should pass


def test_invalid_attribute(tmp_path):
    cs = ChunkStore(str(tmp_path / "chunks.json"))
    ni = NameIndex(str(tmp_path / "index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))

    ts.create_type("PIPE", {
        "name": "string"
    })

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = DBEngine(str(tmp_path / "db.json"), cs, ni, ts, gindex)

    from opecore.model.node import Node

    node = Node(attributes={
        "type": "PIPE",
        "invalid": 10
    })

    try:
        db.create_node(node)
        assert False
    except ValueError:
        assert True

def test_invalid_type(tmp_path):
    cs = ChunkStore(str(tmp_path / "chunks.json"))
    ni = NameIndex(str(tmp_path / "index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = DBEngine(str(tmp_path / "db.json"), cs, ni, ts, gindex)

    node = Node(attributes={
        "type": "UNKNOWN",
        "name": "x"
    })

    try:
        db.create_node(node)
        assert False
    except ValueError:
        assert True


