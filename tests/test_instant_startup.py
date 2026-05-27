import tempfile
import os
from opecore.storage.log import FileManager
from opecore.index.btree import BTree


def test_instant_startup():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            tree = BTree(fm)
            tree.insert(1, 100)
            tree.insert(2, 200)

        # reopen (no scan should be needed)
        with FileManager(path) as fm:
            tree = BTree(fm)

            assert tree.search(1) == 100
            assert tree.search(2) == 200
