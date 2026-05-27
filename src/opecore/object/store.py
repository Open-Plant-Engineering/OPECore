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

    def put(self, *, fields, parent_id=None):
        object_id = self.id_gen.generate()
        ts = self.id_gen.decode(object_id)["timestamp"]
        node_id = self.id_gen.decode(object_id)["node_id"]

        encoded, _ = encode_object(
            object_id=object_id,
            parent_id=parent_id,
            fields=fields,
            timestamp=ts,
            node_id=node_id,
        )

        offset = self.fm.append_record(OBJECT_RECORD, encoded)
        self.index[object_id] = offset

        return object_id

    def get(self, object_id):
        offset = self.index[object_id]
        _, payload = self.fm.read_at(offset)

        obj = decode_object(payload)

        if obj["object_id"] != object_id:
            raise ValueError("Object mismatch")

        return obj
