from opecore.wal.wal_queue import WALQueue
from opecore.db.json_db import JsonDB
from opecore.leader.worker import LeaderWorker


def test_full_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    db = JsonDB(str(tmp_path / "main.db"))
    worker = LeaderWorker(wal, db)

    # create work
    work = wal.create_work()

    # submit request
    wal.submit(work, {
        "action": "create",
        "name": "zone1",
        "type": "zone"
    })

    worker.process_once()

    nodes = db.list_nodes()

    assert len(nodes) == 1
    assert nodes[0].name == "zone1"
