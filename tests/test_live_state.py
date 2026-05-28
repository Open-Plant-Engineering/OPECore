from opecore.storage.log import AppendOnlyLog
from opecore.queue.queue import RequestQueue
from opecore.claims.claims import ClaimManager
from opecore.leader.leader import Leader
from opecore.leader.worker import LeaderWorker
from opecore.recovery.idempotency import IdempotencyStore
from opecore.state.store import StateStore


def test_live_state_updates(tmp_path):
    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimManager(str(db))
    leader = Leader(str(db))
    idem = IdempotencyStore(str(db))
    state = StateStore(log)

    leader.try_become_leader()

    worker = LeaderWorker(log, queue, claims, leader, idem, state)

    # No manual load() call needed
    queue.submit({
        "action": "set",
        "path": "/a",
        "value": 100
    })

    worker.process_once()

    # ✅ Immediately available
    assert state.get("/a") == 100

def test_lazy_load_then_live(tmp_path):
    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))

    # Pre-existing record
    import json
    log.append(json.dumps({
        "op": "SET",
        "path": "/init",
        "value": 1
    }).encode())

    queue = RequestQueue(str(db / "queue"))
    claims = ClaimManager(str(db))
    leader = Leader(str(db))
    idem = IdempotencyStore(str(db))
    state = StateStore(log)

    leader.try_become_leader()

    worker = LeaderWorker(log, queue, claims, leader, idem, state)

    # First read → triggers load
    assert state.get("/init") == 1

    # Now update live
    queue.submit({
        "action": "set",
        "path": "/init",
        "value": 2
    })

    worker.process_once()

    # ✅ instant update, no replay
    assert state.get("/init") == 2

