from opecore.wal.wal_queue import WALQueue
import os


def test_wal_lifecycle(tmp_path):
    wal = WALQueue(str(tmp_path))

    # user creates work
    work = wal.create_work()

    # submit
    req = wal.submit(work, {"action": "set", "path": "/a", "value": 1})

    files = wal.list_requests()
    assert len(files) == 1

    # leader process
    p = wal.mark_processing(files[0])
    assert p.endswith(".processing")

    wal.mark_done(p)

    assert any(f.endswith(".done") for f in os.listdir(tmp_path))