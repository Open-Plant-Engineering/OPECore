import os
import tempfile
from opecore.v1.infra.file_manager import FileManager


def test_file_manager_write_read():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)

        offset = fm.append_record(1, b"hello")

        rtype, payload = fm.read_at(offset)

        assert rtype == 1
        assert payload == b"hello"

        fm.close()


def test_txn_record():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)

        offset = fm.append_txn_record(2, 123, b"data")

        rtype, txn_id, data = fm.read_txn_record(offset)

        assert rtype == 2
        assert txn_id == 123
        assert data == b"data"

        fm.close()


def test_scan_records():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)

        fm.append_record(1, b"a")
        fm.append_record(1, b"b")

        records = list(fm.scan_records())

        assert len(records) >= 2

        fm.close()