import tempfile
import os

from opecore.v1.infra.file_manager import FileManager
from opecore.v1.storage.btree import BTree


def test_insert_and_search():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        tree = BTree(fm)

        for i in range(10):
            tree.insert(i, i * 10, txn_id=1)

        for i in range(10):
            assert tree.search(i) == i * 10

        fm.close()


def test_range_query():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        fm = FileManager(path)
        tree = BTree(fm)

        for i in range(10):
            tree.insert(i, i, txn_id=1)

        res = tree.range(3, 6)

        assert set(res) == {3, 4, 5, 6}

        fm.close()
