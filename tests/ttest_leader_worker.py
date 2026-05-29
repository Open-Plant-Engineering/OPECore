from opecore.storage.log import AppendOnlyLog
from opecore.queue.queue import RequestQueue
from opecore.claims.claim_engine import ClaimEngine
from opecore.leader.leader import Leader
from opecore.leader.op_engine import OPEngine
from opecore.recovery.idempotency import IdempotencyStore

def test_leader_process_claim(tmp_path):
    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimEngine(str(db))
    leader = Leader(str(db))

    assert leader.try_become_leader()

    idem = IdempotencyStore(str(db))
    worker = OPEngine(log, queue, claims, leader, idem)

    # Submit request
    queue.submit({
        "action": "claim",
        "user": "u1",
        "path": "/a",
        "type": "EXACT"
    })

    worker.process_once()

    # Validate claim applied
    all_claims = claims.load()
    assert len(all_claims) == 1
    assert all_claims[0]["path"] == "/a"


def test_leader_append(tmp_path):
    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimEngine(str(db))
    leader = Leader(str(db))

    leader.try_become_leader()

    idem = IdempotencyStore(str(db))
    worker = OPEngine(log, queue, claims, leader, idem)

    rid = "test-id-123"

    queue.submit({
        "action": "set",
        "path": "/test",
        "value": {"x": 1},
        "request_id": rid
    })

    worker.process_once()

    records = log.replay()

    assert len(records) == 1

def test_same_request_id_only_executes_once(tmp_path):
    from opecore.recovery.idempotency import IdempotencyStore
    from opecore.storage.log import AppendOnlyLog
    from opecore.queue.queue import RequestQueue
    from opecore.claims.claim_engine import ClaimEngine
    from opecore.leader.leader import Leader
    from opecore.leader.op_engine import OPEngine

    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimEngine(str(db))
    leader = Leader(str(db))
    idem = IdempotencyStore(str(db))

    leader.try_become_leader()

    worker = OPEngine(log, queue, claims, leader, idem)

    rid = "test-id-123"

    queue.submit({
        "action": "set",
        "path": "/test",
        "value": {"x": 1},
        "request_id": rid
    })

    queue.submit({
        "action": "set",
        "path": "/test",
        "value": {"x": 1},
        "request_id": rid
    })

    worker.process_once()

    assert len(log.replay()) == 1
    
from opecore.state.store import StateStore


def test_set_updates_state(tmp_path):
    from opecore.storage.log import AppendOnlyLog
    from opecore.queue.queue import RequestQueue
    from opecore.claims.claim_engine import ClaimEngine
    from opecore.leader.leader import Leader
    from opecore.leader.op_engine import OPEngine
    from opecore.recovery.idempotency import IdempotencyStore

    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimEngine(str(db))
    leader = Leader(str(db))
    idem = IdempotencyStore(str(db))

    leader.try_become_leader()

    worker = OPEngine(log, queue, claims, leader, idem)

    queue.submit({
        "action": "set",
        "path": "/a",
        "value": {"x": 42}
    })

    worker.process_once()

    store = StateStore(log)
    store.load()

    assert store.get("/a") == {"x": 42}