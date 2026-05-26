import struct
import os
import time
import json
from typing import Optional, Dict
from opecore.storage.wal import WAL


class StorageEngine:
    """
    Append-only storage engine with version chaining.
    """

    HEADER_FORMAT = "QQdqI"
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, path: str = "data.db"):
        self.path = path

        # ✅ WAL must be separate file
        self.wal = WAL(path + ".wal")

        self.head_index: Dict[int, int] = {}
        self.version_counter = 0

        self.recover_from_wal()
        self._load_index()

    # ✅ ===============================
    # LOAD FILE → BUILD HEAD INDEX
    # ✅ ===============================

    def _load_index(self):
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

                    f.seek(size, 1)

                    self.head_index[object_id] = offset

                    if version_id > self.version_counter:
                        self.version_counter = version_id

                    offset += self.HEADER_SIZE + size

        except FileNotFoundError:
            pass

    # ✅ ===============================
    # WRITE
    # ✅ ===============================

    def append(self, object_id: int, data: bytes) -> int:
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
            f.flush()
            os.fsync(f.fileno())

        self.head_index[object_id] = offset
        return offset

    # ✅ ===============================
    # READ
    # ✅ ===============================

    def read_latest(self, object_id: int) -> Optional[bytes]:
        offset = self.head_index.get(object_id)

        if offset is None:
            return None

        try:
            return self._read_record(offset)["data"]
        except Exception:
            return None

    def read_as_of(self, object_id: int, timestamp: float) -> Optional[bytes]:
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
    # DEBUG
    # ✅ ===============================

    def read_all(self):
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

    # ✅ ===============================
    # WAL RECOVERY
    # ✅ ===============================

    def recover_from_wal(self):
        records = self.wal.read_all()

        txn_map = {}

        for rec in records:
            txn_id = rec["txn_id"]

            if txn_id not in txn_map:
                txn_map[txn_id] = {}

            txn_map[txn_id][rec["state"]] = rec

        for txn_id, states in txn_map.items():

            if "PREPARE" in states:
                changes = states["PREPARE"]["changes"]

                for object_id, updates in changes.items():
                    try:
                        obj_id = int(object_id)

                        # ✅ convert dict → bytes
                        data = json.dumps(updates).encode()

                        self.append(obj_id, data)

                    except Exception:
                        pass

        # ✅ Clear WAL after recovery
        self.wal.clear()
