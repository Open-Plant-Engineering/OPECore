import time
import struct


class StorageEngine:
    def __init__(self, path="data.db"):
        self.path = path

    def append(self, object_id: int, data: bytes):
        timestamp = int(time.time())

        with open(self.path, "ab") as f:
            record = struct.pack("QQI", object_id, timestamp, len(data))
            f.write(record)
            f.write(data)

    def read_all(self):
        records = []
        with open(self.path, "rb") as f:
            while True:
                header = f.read(20)
                if not header:
                    break

                object_id, timestamp, size = struct.unpack("QQI", header)
                data = f.read(size)

                records.append((object_id, timestamp, data))

        return records
