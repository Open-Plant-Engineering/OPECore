from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.store import ObjectStore
from opecore.index.btree import BTree
from opecore.txn.manager import TransactionManager
from opecore.recovery.rebuilder import RecoveryManager


class StorageEngine:
    def __init__(self, path):
        self.path = path

        self.fm = FileManager(path)
        self.txn = TransactionManager(self.fm)

        self.chunk = ChunkStore(self.fm)
        self.obj = ObjectStore(self.fm, self.chunk)

        self.index = BTree(self.fm)
        self.sec_index = BTree(self.fm)

        # ✅ rebuild from WAL
        self._recover()

    def _recover(self):
        RecoveryManager(self.fm, self.chunk, self.obj).rebuild()

    def begin(self):
        return self.txn.begin()

    def commit(self, tid):
        self.txn.commit(tid)

    def close(self):
        if self.fm:
            try:
                self.fm.close()
            except:
                pass