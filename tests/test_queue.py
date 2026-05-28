import os
import json
from opecore.queue.queue import RequestQueue


def test_submit_and_list(tmp_path):
    q = RequestQueue(str(tmp_path))

    req_id = q.submit({"action": "test"})

    files = q.list_requests()

    assert len(files) == 1
    assert files[0].endswith(".req")


def test_mark_processing(tmp_path):
    q = RequestQueue(str(tmp_path))

    q.submit({"action": "test"})

    files = q.list_requests()
    fname = files[0]

    processing_path = q.mark_processing(fname)

    assert os.path.exists(processing_path)
    assert processing_path.endswith(".processing")


def test_mark_done(tmp_path):
    q = RequestQueue(str(tmp_path))

    q.submit({"action": "test"})
    fname = q.list_requests()[0]

    p = q.mark_processing(fname)
    q.mark_done(p)

    assert os.path.exists(p.replace(".processing", ".done"))


def test_mark_failed(tmp_path):
    q = RequestQueue(str(tmp_path))

    q.submit({"action": "test"})
    fname = q.list_requests()[0]

    p = q.mark_processing(fname)
    q.mark_failed(p)

    assert os.path.exists(p.replace(".processing", ".failed"))

def test_recover_processing(tmp_path):
    from opecore.queue.queue import RequestQueue

    q = RequestQueue(str(tmp_path))

    q.submit({"action": "test"})
    fname = q.list_requests()[0]

    p = q.mark_processing(fname)

    q.recover_stuck()

    files = q.list_requests()

    assert len(files) == 1
