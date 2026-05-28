from opecore.storage.log import AppendOnlyLog
from opecore.queue.queue import RequestQueue
from opecore.claims.claims import ClaimManager
from opecore.leader.leader import Leader
from opecore.leader.worker import LeaderWorker
from opecore.recovery.idempotency import IdempotencyStore


def test_no_duplicate_execution(tmp_path):
    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimManager(str(db))
    leader = Leader(str(db))
    idem = IdempotencyStore(str(db))

    assert leader.try_become_leader()

    worker = LeaderWorker(log, queue, claims, leader, idem)

    rid = "fixed-id-1"
    
    queue.submit({
        "action": "set",
        "path": "/test",
        "value": {"x": 1},
        "request_id": rid
    })
    
    # simulate duplicate request with SAME ID
    queue.submit({
        "action": "set",
        "path": "/test",
        "value": {"x": 1},
        "request_id": rid
    })

    worker.process_once()

    records = log.replay()

    assert len(records) == 1
