import hashlib

CHUNK_RECORD = 1


class ChunkStore:
    def __init__(self, file_manager):
        self.fm = file_manager
        self.index = {}  # chunk_id → offset

    def put(self, data: bytes):
        chunk_id = hashlib.sha256(data).digest()

        if chunk_id in self.index:
            return chunk_id

        payload = chunk_id + data
        offset = self.fm.append_record(CHUNK_RECORD, payload)

        self.index[chunk_id] = offset
        return chunk_id

    def get(self, chunk_id: bytes):
        offset = self.index[chunk_id]
        _, payload = self.fm.read_at(offset)

        stored_id = payload[:32]
        data = payload[32:]

        if stored_id != chunk_id:
            raise ValueError("Chunk integrity error")

        return data
