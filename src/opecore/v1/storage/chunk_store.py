import hashlib


CHUNK_RECORD = 1


class ChunkStore:
    """
    SOLID v1 ChunkStore

    Responsibility:
    - Deduplicate binary data via hashing
    - Store chunks in append-only log
    - Retrieve chunk by id
    """

    def __init__(self, file_manager):
        self.fm = file_manager

        # in-memory index: chunk_id → offset
        self.index = {}

        # simple cache (optional, can swap later)
        self.cache = {}

    # ------------------------
    # WRITE
    # ------------------------

    def put(self, data: bytes, txn_id: int):
        chunk_id = self._hash(data)

        # ✅ deduplication
        if chunk_id in self.index:
            return chunk_id

        payload = chunk_id + data

        offset = self.fm.append_txn_record(
            CHUNK_RECORD,
            txn_id,
            payload
        )

        self.index[chunk_id] = offset

        return chunk_id

    # ------------------------
    # READ
    # ------------------------

    def get(self, chunk_id: bytes):
        # ✅ cache lookup
        if chunk_id in self.cache:
            return self.cache[chunk_id]

        offset = self.index.get(chunk_id)

        if offset is None:
            raise KeyError("Chunk not found")

        _, _, payload = self.fm.read_txn_record(offset)

        stored_id = payload[:32]
        data = payload[32:]

        # ✅ integrity check
        if stored_id != chunk_id:
            raise ValueError("Chunk integrity mismatch")

        self.cache[chunk_id] = data

        return data

    # ------------------------
    # INTERNAL
    # ------------------------

    def _hash(self, data: bytes):
        return hashlib.sha256(data).digest()
