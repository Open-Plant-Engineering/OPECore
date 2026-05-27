from opecore.storage.log import FileManager
from opecore.chunk.store import ChunkStore
from opecore.object.encoder import encode_object
from opecore.object.model import decode_object
from opecore.id.snowflake import SnowflakeGenerator

OBJECT_RECORD = 2


class ObjectStore:
    def __init__(self, file_manager: FileManager, chunk_store: ChunkStore, db_id=1):
        self.fm = file_manager
        self.chunk_store = chunk_store
        self.id_gen = SnowflakeGenerator(db_id)

        self.index = {}  # object_id → offset

    def put(self, *, fields, txn_id, parent_id=None):
        object_id = self.id_gen.generate()
        ts_info = self.id_gen.decode(object_id)

        encoded, _ = encode_object(
            object_id=object_id,
            parent_id=parent_id,
            fields=fields,
            timestamp=ts_info["timestamp"],
            node_id=ts_info["node_id"],
        )

        offset = self.fm.append_txn_record(2, txn_id, encoded)
        self.index[object_id] = offset

        return object_id

    def get(self, object_id):
        offset = self.index[object_id]

        rtype, txn_id, payload = self.fm.read_txn_record(offset)

        obj = decode_object(payload)

        if obj["object_id"] != object_id:
            raise ValueError("Object mismatch")

        return obj
