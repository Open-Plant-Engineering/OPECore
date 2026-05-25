import struct
import time
from typing import Optional, Dict

class StorageEngine:
    HEADER_FORMAT = "QQdqI"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, path: str = "data.db"):
        self.path = path
        self.head_index: Dict[int, int] = {}
        self.version_counter = 0
        self._load_index()

    def _load_index(self):
        try:
            with open(self.path, "rb") as f:
                offset = 0
                while True:
                    header = f.read(self.HEADER_SIZE)
                    if not header:
                        break

                    object_id, version_id, timestamp, parent, size = struct.unpack(self.HEADER_FORMAT, header)
                    f.seek(size, 1)

                    self.head_index[object_id] = offset
                    self.version_counter = max(self.version_counter, version_id)

                    offset += self.HEADER_SIZE + size
        except FileNotFoundError:
            pass

    def append(self, object_id: int, data: bytes):
        timestamp = time.time()
        parent_offset = self.head_index.get(object_id, -1)

        self.version_counter += 1
        version_id = self.version_counter

        with open(self.path, "ab") as f:
            offset = f.tell()

            header = struct.pack(
                self.HEADER_FORMAT,
                object_id,
                version_id,
                timestamp,
                parent_offset,
                len(data),
            )

            f.write(header)
            f.write(data)

        self.head_index[object_id] = offset

    def read_latest(self, object_id: int) -> Optional[bytes]:
        offset = self.head_index.get(object_id)
        if offset is None:
            return None
        return self._read_record(offset)["data"]

    def read_as_of(self, object_id: int, timestamp: float) -> Optional[bytes]:
        offset = self.head_index.get(object_id)

        while offset is not None and offset != -1:
            record = self._read_record(offset)
            if record["timestamp"] <= timestamp:
                return record["data"]
            offset = record["parent"]

        return None

    def _read_record(self, offset: int):
        with open(self.path, "rb") as f:
            f.seek(offset)
            header = f.read(self.HEADER_SIZE)

            object_id, version_id, timestamp, parent, size = struct.unpack(self.HEADER_FORMAT, header)
            data = f.read(size)

            return {
                "object_id": object_id,
                "version_id": version_id,
                "timestamp": timestamp,
                "parent": parent,
                "data": data,
            }
