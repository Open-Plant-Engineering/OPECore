import time
import struct


class StorageEngine:
    HEADER_FORMAT = "QQdqI"   # object_id, timestamp, parent_offset, data_size
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    def __init__(self, path="data.db"):
        self.path = path
        self.head_index = {}  # object_id → latest offset
        self.version_counter = 0

        # rebuild index from file (simple scan for now)
        self._load_index()

    def _load_index(self):
        try:
            with open(self.path, "rb") as f:
                offset = 0

                print("\n--- LOADING INDEX ---")

                while True:
                    header = f.read(self.HEADER_SIZE)
                    if not header:
                        break
                    
                    object_id, version_id, timestamp, parent, size = struct.unpack(
                        self.HEADER_FORMAT, header
                    )

                    print(f"Loaded → object={object_id}, timestamp={timestamp}, parent={parent}")

                    f.seek(size, 1)

                    self.head_index[object_id] = offset

                    offset += self.HEADER_SIZE + size

                print("--- INDEX LOAD COMPLETE ---\n")
        except FileNotFoundError:
            pass

    # ✅ APPEND NEW VERSION
    def append(self, object_id: int, data: bytes):
        timestamp = time.time()

        parent_offset = self.head_index.get(object_id, -1)

        self.version_counter += 1
        version_id = self.version_counter

        print(f"APPEND → obj={object_id}, ver={version_id}, ts={timestamp}, parent={parent_offset}")

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

    # ✅ READ LATEST VERSION
    def read_latest(self, object_id: int):
        offset = self.head_index.get(object_id)

        if offset is None:
            return None

        return self._read_at_offset(offset)

    # ✅ READ AS OF TIME (YOUR MAIN FEATURE)
    def read_as_of(self, object_id: int, timestamp):
        print(f"\n--- READ_AS_OF START ---")
        print(f"Requested timestamp: {timestamp}")
    
        offset = self.head_index.get(object_id)
        print(f"HEAD offset: {offset}")
    
        step = 0
    
        while offset is not None and offset != -1:
            record = self._read_record(offset)
    
            print(f"\nStep {step}")
            print(f"Offset: {offset}")
            print(f"Record timestamp: {record['timestamp']}")
            print(f"Parent offset: {record['parent']}")
            print(f"Data: {record['data']}")
    
            if record["timestamp"] <= timestamp:
                print(f"✅ MATCH FOUND → returning {record['data']}")
                return record["data"]
    
            print("❌ Too new, moving to parent")
            offset = record["parent"]
            step += 1
    
        print("❌ No matching version found")
        return None

    # ✅ INTERNAL READ
    def _read_record(self, offset):
        with open(self.path, "rb") as f:
            f.seek(offset)

            header = f.read(self.HEADER_SIZE)
            object_id, version_id, timestamp, parent, size = struct.unpack(
                self.HEADER_FORMAT, header
            )

            data = f.read(size)

            return {
                "object_id": object_id,
                "timestamp": timestamp,
                "parent": parent,
                "data": data,
            }

    def _read_at_offset(self, offset):
        return self._read_record(offset)["data"]

    def read_all(self):
        records = []

        with open(self.path, "rb") as f:
            offset = 0

            while True:
                header = f.read(self.HEADER_SIZE)
                if not header:
                    break

                object_id, timestamp, parent, size = struct.unpack(
                    self.HEADER_FORMAT, header
                )

                data = f.read(size)

                records.append({
                    "object_id": object_id,
                    "timestamp": timestamp,
                    "parent": parent,
                    "data": data,
                    "offset": offset
                })

                offset += self.HEADER_SIZE + size

        return records