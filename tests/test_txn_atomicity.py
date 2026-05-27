import tempfile, os
from opecore.storage.log import FileManager
from opecore.txn.manager import TransactionManager


def test_uncommitted_data_not_visible():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)

            tid = txn_mgr.begin()

            fm.append_txn_record(99, tid, b"data1")  # simulate write
            # ❌ no commit

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            committed = txn_mgr.recover_committed()

            assert tid not in committed