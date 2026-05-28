from opecore.storage.log import AppendOnlyLog
from opecore.queue.queue import RequestQueue
from opecore.claims.claims import ClaimManager
from opecore.leader.leader import Leader
from opecore.leader.worker import LeaderWorker


def test_leader_process_claim(tmp_path):
    db = tmp_path

    log = AppendOnlyLog(str(db / "data.log"))
    queue = RequestQueue(str(db / "queue"))
    claims = ClaimManager(str(db))
    leader = Leader(str(db))

    assert leader.try_become_leader()

    worker = LeaderWorker(log, queue, claims, leader)

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
    claims = ClaimManager(str(db))
    leader = Leader(str(db))

    leader.try_become_leader()

    worker = LeaderWorker(log, queue, claims, leader)

    queue.submit({
        "action": "append",
        "data": {"x": 10}
    })

    worker.process_once()

    records = log.replay()

    assert len(records) == 1