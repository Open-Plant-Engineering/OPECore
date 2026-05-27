import tempfile
import os
from opecore.storage.log import FileManager
from opecore.txn.manager import TransactionManager


def test_txn_commit():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn = TransactionManager(fm)

            tid = txn.begin()
            txn.commit(tid)

        with FileManager(path) as fm:
            txn = TransactionManager(fm)

            committed = txn.recover_committed()

            assert tid in committed


def test_txn_incomplete():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn = TransactionManager(fm)

            tid = txn.begin()
            # ❌ no commit

        with FileManager(path) as fm:
            txn = TransactionManager(fm)

            committed = txn.recover_committed()

            assert tid not in committed