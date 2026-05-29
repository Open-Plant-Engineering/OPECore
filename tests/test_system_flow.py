from opecore.wal.wal_queue import WALQueue
from opecore.db.json_db import JsonDB
from opecore.leader.worker import LeaderWorker
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex


def test_create_node_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))

    ts.create_type("zone", {
        "name": "string",
        "owner": "ref"
    })

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    worker = LeaderWorker(wal, db)

    # ✅ create owner node first
    from opecore.model.node import Node

    owner = Node(attributes={
        "type": "zone",
        "name": "owner_node"
    })
    db.create_node(owner)

    # User creates work file
    work = wal.create_work()

    # ✅ use valid refno
    wal.submit(work, {
        "action": "create",
        "name": "zone1",
        "type": "zone",
        "owner": owner.refno
    })

    worker.process_once()

    nodes = db.list_nodes()

    assert len(nodes) == 2   # owner + zone1
    assert nodes[1].attributes["name"] == "zone1"


def test_update_node_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    ts.create_type("x", {
        "name": "string"
    })
    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    worker = LeaderWorker(wal, db)

    # Create
    work = wal.create_work()
    wal.submit(work, {
        "action": "create",
        "name": "a",
        "type": "x"
    })

    worker.process_once()

    node = db.list_nodes()[0]

    # Update
    work = wal.create_work()
    wal.submit(work, {
        "action": "update",
        "refno": node.refno,
        "name": "updated"
    })

    worker.process_once()

    updated = db.get_node(node.refno)

    assert updated.attributes["name"] == "updated"

def test_delete_node_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    ts.create_type("x", {
        "name": "string"
    })

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = JsonDB(str(tmp_path / "db.json"), store, index, ts, gindex)

    worker = LeaderWorker(wal, db)

    # Create
    work = wal.create_work()
    wal.submit(work, {
        "action": "create",
        "name": "a",
        "type": "x"
    })

    worker.process_once()

    node = db.list_nodes()[0]

    # Delete
    work = wal.create_work()
    wal.submit(work, {
        "action": "delete",
        "refno": node.refno
    })

    worker.process_once()

    assert db.get_node(node.attributes["refno"]) is None
