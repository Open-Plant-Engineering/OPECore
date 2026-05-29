from opecore.wal.wal_queue import WALQueue
from opecore.db.json_db import JsonDB
from opecore.leader.worker import LeaderWorker
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore


def test_create_node_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    ts.create_type("zone", {
        "name": "string",
        "owner": "string"
    })

    db = JsonDB(str(tmp_path / "main.db"), store, index, ts)
    worker = LeaderWorker(wal, db)

    # User creates work file
    work = wal.create_work()

    # Submit request
    wal.submit(work, {
        "action": "create",
        "name": "zone1",
        "type": "zone",
        "owner": "user1"
    })

    # Leader processes
    worker.process_once()

    # Validate DB
    nodes = db.list_nodes()

    assert len(nodes) == 1
    assert nodes[0].attributes["name"] == "zone1"


def test_update_node_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    ts.create_type("x", {
        "name": "string"
    })
    db = JsonDB(str(tmp_path / "main.db"), store, index, ts)
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

    db = JsonDB(str(tmp_path / "main.db"), store, index, ts)
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
