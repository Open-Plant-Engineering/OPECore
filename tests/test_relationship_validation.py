from opecore.model.node import Node
from opecore.db.json_db import DBEngine
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex

def setup_db(tmp_path):
    cs = ChunkStore(str(tmp_path / "chunks.json"))
    ni = NameIndex(str(tmp_path / "index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))

    ts.create_type("ITEM", {
        "name": "string",
        "parent": "ref",
        "owner": "ref"
    })

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = DBEngine(str(tmp_path / "db.json"), cs, ni, ts, gindex)
    return db


# ✅ TEST 1 — valid root node (no parent, no owner)
def test_root_node_allowed(tmp_path):
    db = setup_db(tmp_path)

    node = Node(attributes={
        "type": "ITEM",
        "name": "root"
    })

    db.create_node(node)

    assert len(db.list_nodes()) == 1


# ✅ TEST 2 — valid parent-child
def test_valid_parent(tmp_path):
    db = setup_db(tmp_path)

    parent = Node(attributes={
        "type": "ITEM",
        "name": "parent"
    })
    db.create_node(parent)

    child = Node(attributes={
        "type": "ITEM",
        "name": "child",
        "parent": parent.refno
    })

    db.create_node(child)

    assert len(db.list_nodes()) == 2


# ✅ TEST 3 — parent must exist
def test_invalid_parent(tmp_path):
    db = setup_db(tmp_path)

    node = Node(attributes={
        "type": "ITEM",
        "name": "child",
        "parent": "fake_ref"
    })

    try:
        db.create_node(node)
        assert False
    except ValueError:
        assert True


# ✅ TEST 4 — owner must exist
def test_invalid_owner(tmp_path):
    db = setup_db(tmp_path)

    node = Node(attributes={
        "type": "ITEM",
        "name": "node",
        "owner": "fake_ref"
    })

    try:
        db.create_node(node)
        assert False
    except ValueError:
        assert True


# ✅ TEST 5 — valid owner reference
def test_valid_owner(tmp_path):
    db = setup_db(tmp_path)

    owner = Node(attributes={
        "type": "ITEM",
        "name": "owner"
    })
    db.create_node(owner)

    node = Node(attributes={
        "type": "ITEM",
        "name": "child",
        "owner": owner.refno
    })

    db.create_node(node)

    assert len(db.list_nodes()) == 2


# ✅ TEST 6 — no self-parent
def test_self_parent_invalid(tmp_path):
    db = setup_db(tmp_path)

    node = Node(attributes={
        "type": "ITEM",
        "name": "node"
    })

    # force self-parent
    node.attributes["parent"] = node.refno

    try:
        db.create_node(node)
        assert False
    except ValueError:
        assert True


# ✅ TEST 7 — ref attribute validation
def test_valid_ref_attribute(tmp_path):
    db = setup_db(tmp_path)

    target = Node(attributes={
        "type": "ITEM",
        "name": "target"
    })
    db.create_node(target)

    node = Node(attributes={
        "type": "ITEM",
        "name": "node",
        "owner": target.refno   # owner is also ref type
    })

    db.create_node(node)

    assert len(db.list_nodes()) == 2


# ✅ TEST 8 — missing ref allowed (treated as root/no link)
def test_none_ref_allowed(tmp_path):
    db = setup_db(tmp_path)

    node = Node(attributes={
        "type": "ITEM",
        "name": "node",
        "parent": None
    })

    db.create_node(node)

    assert len(db.list_nodes()) == 1


# ✅ TEST 9 — update with invalid parent should fail
def test_update_invalid_parent(tmp_path):
    db = setup_db(tmp_path)

    node = Node(attributes={
        "type": "ITEM",
        "name": "node"
    })
    db.create_node(node)

    node.attributes["parent"] = "fake_ref"

    try:
        db.update_node(node)
        assert False
    except ValueError:
        assert True


# ✅ TEST 10 — update with valid parent works
def test_update_valid_parent(tmp_path):
    db = setup_db(tmp_path)

    parent = Node(attributes={
        "type": "ITEM",
        "name": "parent"
    })
    db.create_node(parent)

    node = Node(attributes={
        "type": "ITEM",
        "name": "child"
    })
    db.create_node(node)

    node.attributes["parent"] = parent.refno

    db.update_node(node)

    updated = db.get_node(node.refno)

    assert updated.attributes["parent"] == parent.refno
