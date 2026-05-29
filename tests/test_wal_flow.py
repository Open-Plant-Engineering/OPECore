from opecore.wal.wal_queue import QueueEngine
from opecore.db.json_db import DBEngine
from opecore.leader.op_engine import OPEngine
from opecore.storage.chunk_store import ChunkStore
from opecore.storage.name_index import NameIndex
from opecore.storage.type_store import TypeStore
from opecore.storage.generic_index import GenericIndex


def test_full_flow(tmp_path):
    wal = QueueEngine(str(tmp_path / "wal"))
    store = ChunkStore(str(tmp_path / "chunks.json"))
    index = NameIndex(str(tmp_path / "name_index.json"))
    ts = TypeStore(str(tmp_path / "types.json"))
    ts.create_type("zone", {
        "name": "string",
    })

    gindex = GenericIndex(str(tmp_path / "gindex.json"))
    db = DBEngine(str(tmp_path / "db.json"), store, index, ts, gindex)
    
    worker = OPEngine(wal, db)

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
