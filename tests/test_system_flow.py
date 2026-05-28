from opecore.wal.wal_queue import WALQueue
from opecore.db.json_db import JsonDB
from opecore.leader.worker import LeaderWorker


def test_create_node_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    db = JsonDB(str(tmp_path / "main.db"))
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
    assert nodes[0].name == "zone1"