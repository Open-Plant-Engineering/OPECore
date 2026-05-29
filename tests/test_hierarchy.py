from opecore.db.json_db import JsonDB
from opecore.model.node import Node
from opecore.db.hierarchy import get_children, get_parent, get_subtree
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.wal.wal_queue import WALQueue
from opecore.leader.worker import LeaderWorker
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex


def test_parent_child(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    parent = Node(attributes={"name": "parent"})
    db.create_node(parent)

    child = Node(attributes={
        "name": "child",
        "parent": parent.refno
    })
    db.create_node(child)

    children = get_children(db, parent.refno)

    assert len(children) == 1
    assert children[0].attributes["name"] == "child"


def test_get_parent(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    parent = Node(attributes={"name": "p"})
    db.create_node(parent)

    child = Node(attributes={
        "name": "c",
        "parent": parent.refno
    })
    db.create_node(child)

    p = get_parent(db, child.refno)

    assert p.refno == parent.refno


def test_subtree(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    root = Node(attributes={"name": "root"})
    db.create_node(root)

    c1 = Node(attributes={"name": "c1", "parent": root.refno})
    c2 = Node(attributes={"name": "c2", "parent": root.refno})
    c3 = Node(attributes={"name": "c3", "parent": c1.refno})

    db.create_node(c1)
    db.create_node(c2)
    db.create_node(c3)

    subtree = get_subtree(db, root.refno)

    # c1, c2, c3
    assert len(subtree) == 3

def test_wal_hierarchy(tmp_path):

    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)
    
    worker = LeaderWorker(wal, db)

    # Create parent
    work = wal.create_work()
    wal.submit(work, {
        "action": "create",
        "name": "root"
    })

    worker.process_once()

    root = db.list_nodes()[0]

    # Create child
    work = wal.create_work()
    wal.submit(work, {
        "action": "create",
        "name": "child",
        "parent": root.refno
    })

    worker.process_once()

    children = get_children(db, root.refno)

    assert len(children) == 1
