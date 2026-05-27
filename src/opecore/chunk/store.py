import hashlib
from opecore.cache.lru import LRUCache


CHUNK_RECORD = 1


class ChunkStore:
    def __init__(self, file_manager):
        self.fm = file_manager
        self.index = {}  # chunk_id → offset
        self.cache = LRUCache(10000)

    def put(self, data: bytes, txn_id: int):
        chunk_id = hashlib.sha256(data).digest()

        if chunk_id in self.index:
            return chunk_id

        payload = chunk_id + data
        offset = self.fm.append_txn_record(CHUNK_RECORD, txn_id, payload)

        self.index[chunk_id] = offset

        return chunk_id

    def get(self, chunk_id: bytes):
        cached = self.cache.get(chunk_id)
        if cached:
            return cached

        offset = self.index[chunk_id]
        _, _, payload = self.fm.read_txn_record(offset)

        stored_id = payload[:32]
        data = payload[32:]

        if stored_id != chunk_id:
            raise ValueError("Chunk integrity error")

        self.cache.put(chunk_id, data)

        return data
