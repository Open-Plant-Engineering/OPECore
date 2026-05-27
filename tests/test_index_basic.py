import tempfile
import os
from opecore.storage.log import FileManager
from opecore.index.btree import BTree


def test_insert_and_search():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        with FileManager(path) as fm:
            tree = BTree(fm)

            data = [10, 5, 20, 15, 25]

            for d in data:
                tree.insert(d, d * 10)

            for d in data:
                assert tree.search(d) == d * 10
