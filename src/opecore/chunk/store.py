import hashlib

class ChunkStore:
    def __init__(self, file_manager):
        self.fm = file_manager
        self.index = {}  # chunk_id → offset

    def put(self, data: bytes):
        chunk_id = hashlib.sha256(data).digest()

        if chunk_id in self.index:
            return chunk_id

        offset = self.fm.append_record(1, chunk_id + data)
        self.index[chunk_id] = offset

        return chunk_id

    def get(self, chunk_id: bytes):
        offset = self.index[chunk_id]
        return self.fm.read_chunk(offset)