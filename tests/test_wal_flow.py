from opecore.wal.wal_queue import WALQueue
from opecore.db.json_db import JsonDB
from opecore.leader.worker import LeaderWorker
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex


def test_full_flow(tmp_path):
    wal = WALQueue(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    db = JsonDB(str(tmp_path / "main.db"), store, index)
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
    assert nodes[0].attributes["name"] == "zone1"
