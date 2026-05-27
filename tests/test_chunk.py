from opecore.chunk.store import ChunkStore

class DummyFM:
    def __init__(self):
        self.data = []

    def append_record(self, t, p):
        self.data.append(p)
        return len(self.data) - 1

def test_dedup():
    fm = DummyFM()
    store = ChunkStore(fm)

    a = store.put(b"hello")
    b = store.put(b"hello")

    assert a == b