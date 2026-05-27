import tempfile
import os
from opecore.storage.log import FileManager
from opecore.index.btree import BTree


def test_recovery_from_root():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        # first session
        with FileManager(path) as fm:
            tree = BTree(fm)

            tree.insert(10, 100)
            tree.insert(20, 200)

        # simulate restart
        with FileManager(path) as fm:
            tree = BTree(fm)

            assert tree.search(10) == 100
            assert tree.search(20) == 200