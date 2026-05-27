import tempfile
import os
from opecore.storage.log import FileManager
from opecore.index.btree import BTree
from opecore.txn.manager import TransactionManager


def test_insert_and_search():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            txn_mgr = TransactionManager(fm)
            tree = BTree(fm)

            data = [10, 5, 20, 15, 25]

            tid = txn_mgr.begin()

            for d in data:
                tree.insert(d, d * 10, tid)

            txn_mgr.commit(tid)

            for d in data:
                assert tree.search(d) == d * 10
