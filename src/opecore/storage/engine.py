import struct
import time
from typing import Optional, Dict


class StorageEngine:
    """
    Append-only storage engine with version chaining.

    Each record:
        [HEADER][DATA]

    HEADER format:
        object_id (Q)
        version_id (Q)
        timestamp (d)
        parent_offset (q)
        data_size (I)
    """

    HEADER_FORMAT = "QQdqI"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, path: str = "data.db"):
        self.path = path
        self.head_index: Dict[int, int] = {}  # object_id -> latest offset
        self.version_counter = 0

        self._load_index()

    # ✅ ===============================
    # LOAD FILE → BUILD HEAD INDEX
    # ✅ ===============================

    def _load_index(self):
        """
        Scan entire file and rebuild:
        - head_index (latest version per object)
        - version_counter (max version seen)
        """
        try:
            with open(self.path, "rb") as f:
                offset = 0

                while True:
                    header = f.read(self.HEADER_SIZE)
                    if not header:
                        break

                    (
                        object_id,
                        version_id,
                        timestamp,
                        parent_offset,
                        size,
                    ) = struct.unpack(self.HEADER_FORMAT, header)

                    # skip data
                    f.seek(size, 1)

                    # update latest pointer
                    self.head_index[object_id] = offset

                    # keep version monotonic
                    if version_id > self.version_counter:
                        self.version_counter = version_id

                    offset += self.HEADER_SIZE + size

        except FileNotFoundError:
            # first run → file doesn't exist yet
            pass

    # ✅ ===============================
    # WRITE (APPEND)
    # ✅ ===============================

    def append(self, object_id: int, data: bytes) -> int:
        """
        Append a new version.

        Returns:
            offset of the newly written record
        """
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

        return offset

    # ✅ ===============================
    # READ APIs
    # ✅ ===============================

    def read_latest(self, object_id: int) -> Optional[bytes]:
        offset = self.head_index.get(object_id)
        if offset is None:
            return None

        return self._read_record(offset)["data"]

    def read_as_of(self, object_id: int, timestamp: float) -> Optional[bytes]:
        """
        Return the latest version whose timestamp <= given timestamp
        """
        offset = self.head_index.get(object_id)

        while offset is not None and offset != -1:
            record = self._read_record(offset)

            if record["timestamp"] <= timestamp:
                return record["data"]

            offset = record["parent"]

        return None

    # ✅ ===============================
    # INTERNAL READ
    # ✅ ===============================

    def _read_record(self, offset: int) -> dict:
        with open(self.path, "rb") as f:
            f.seek(offset)

            header = f.read(self.HEADER_SIZE)

            if not header:
                raise ValueError(f"Invalid read at offset {offset}")

            (
                object_id,
                version_id,
                timestamp,
                parent_offset,
                size,
            ) = struct.unpack(self.HEADER_FORMAT, header)

            data = f.read(size)

            return {
                "object_id": object_id,
                "version_id": version_id,
                "timestamp": timestamp,
                "parent": parent_offset,
                "data": data,
            }

    # ✅ ===============================
    # DEBUG / DEV ONLY
    # ✅ ===============================

    def read_all(self):
        """
        Debug utility — sequential scan of all records.
        """
        records = []

        try:
            with open(self.path, "rb") as f:
                offset = 0

                while True:
                    header = f.read(self.HEADER_SIZE)
                    if not header:
                        break

                    (
                        object_id,
                        version_id,
                        timestamp,
                        parent_offset,
                        size,
                    ) = struct.unpack(self.HEADER_FORMAT, header)

                    data = f.read(size)

                    records.append(
                        {
                            "object_id": object_id,
                            "version_id": version_id,
                            "timestamp": timestamp,
                            "parent": parent_offset,
                            "data": data,
                            "offset": offset,
                        }
                    )

                    offset += self.HEADER_SIZE + size

        except FileNotFoundError:
            pass

        return records
