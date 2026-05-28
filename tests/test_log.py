import os
import pytest
from opecore.storage.log import AppendOnlyLog


@pytest.fixture
def log_path(tmp_path):
    return tmp_path / "data.log"


def test_append_and_replay(log_path):
    log = AppendOnlyLog(str(log_path))

    log.append(b"hello")
    log.append(b"world")

    records = log.replay()

    assert records == [b"hello", b"world"]


def test_empty_log(log_path):
    log = AppendOnlyLog(str(log_path))

    records = log.replay()

    assert records == []


def test_multiple_records(log_path):
    log = AppendOnlyLog(str(log_path))

    for i in range(10):
        log.append(f"msg-{i}".encode())

    records = log.replay()

    assert len(records) == 10
    assert records[0] == b"msg-0"
    assert records[-1] == b"msg-9"

def test_corruption_handling(log_path):
    log = AppendOnlyLog(str(log_path))

    log.append(b"A")
    log.append(b"B")

    # Simulate crash corruption
    with open(log_path, "ab") as f:
        f.write(b"corrupt_partial_data")

    records = log.replay()

    # Should stop safely, only valid records preserved
    assert records == [b"A", b"B"]

def test_partial_record_truncation(log_path):
    log = AppendOnlyLog(str(log_path))

    log.append(b"valid1")
    log.append(b"valid2")

    # Truncate file mid-record
    with open(log_path, "rb+") as f:
        content = f.read()
        f.seek(0)
        f.write(content[:-5])  # cut inside second record
        f.truncate()

    records = log.replay()

    # Only first record should survive
    assert records == [b"valid1"]