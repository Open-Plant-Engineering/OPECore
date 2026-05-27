import tempfile
import os
from opecore.storage.log import FileManager
from opecore.index.btree import BTree
from opecore.txn.manager import TransactionManager


def test_recovery_from_root():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        # first run
        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            tree = BTree(fm)

            tid = txn_mgr.begin()

            tree.insert(10, 100, tid)
            tree.insert(20, 200, tid)

            txn_mgr.commit(tid)

        # restart
        with FileManager(path) as fm:
            tree = BTree(fm)

            assert tree.search(10) == 100
            assert tree.search(20) == 200
