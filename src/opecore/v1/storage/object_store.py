OBJECT_RECORD = 2


class ObjectStore:
    """
    SOLID v1 ObjectStore

    Responsibility:
    - Store structured objects as references to chunks
    - Retrieve objects from storage
    - Maintain object_id → offset index

    Does NOT handle:
    - versioning
    - business logic
    - indexing (btree)
    """

    def __init__(self, file_manager, chunk_store, id_generator):
        self.fm = file_manager
        self.chunk = chunk_store
        self.id_gen = id_generator

        # object_id → offset
        self.index = {}

        # simple in-memory cache
        self.cache = {}

    # ------------------------
    # WRITE
    # ------------------------

    def put(self, fields, txn_id, parent_id=None):
        """
        fields = [(key_chunk_id, type, value_chunk_id), ...]
        """
        object_id = self.id_gen.generate()

        payload = self._encode(object_id, parent_id, fields)

        offset = self.fm.append_txn_record(
            OBJECT_RECORD,
            txn_id,
            payload
        )

        self.index[object_id] = offset

        return object_id

    # ------------------------
    # READ
    # ------------------------

    def get(self, object_id):
        if object_id in self.cache:
            return self.cache[object_id]

        offset = self.index.get(object_id)

        if offset is None:
            raise KeyError("Object not found")

        _, _, payload = self.fm.read_txn_record(offset)

        obj = self._decode(payload)

        if obj["object_id"] != object_id:
            raise ValueError("Object mismatch")

        self.cache[object_id] = obj

        return obj

    # ------------------------
    # INTERNAL ENCODE / DECODE
    # ------------------------

    def _encode(self, object_id, parent_id, fields):
        """
        Simple binary encoding:
        [object_id (16 bytes)][parent_id (16 bytes or 0)][num_fields][...fields]
        """

        parent = 0 if parent_id is None else parent_id

        data = (
            object_id.to_bytes(16, "little") +
            parent.to_bytes(16, "little") +
            len(fields).to_bytes(4, "little")
        )

        for key, typ, val in fields:
            data += key + typ.to_bytes(1, "little") + val

        return data

    def _decode(self, payload):
        object_id = int.from_bytes(payload[:16], "little")
        parent_id = int.from_bytes(payload[16:32], "little")
        if parent_id == 0:
            parent_id = None

        num_fields = int.from_bytes(payload[32:36], "little")

        pos = 36
        fields = []

        for _ in range(num_fields):
            key = payload[pos:pos+32]
            pos += 32

            typ = payload[pos]
            pos += 1

            val = payload[pos:pos+32]
            pos += 32

            fields.append((key, typ, val))

        return {
            "object_id": object_id,
            "parent_id": parent_id,
            "fields": fields,
        }
