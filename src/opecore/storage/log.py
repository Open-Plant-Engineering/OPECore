import os
import struct
import zlib


class AppendOnlyLog:
    def __init__(self, path):
        self.path = path

        # Ensure directory exists
        os.makedirs(os.path.dirname(path), exist_ok=True)

        # Ensure file exists
        if not os.path.exists(path):
            open(path, "wb").close()

    def append(self, data: bytes):
        """
        Append a single record:
        [length][data][checksum]
        """
        length = len(data)
        checksum = zlib.crc32(data)

        record = struct.pack(">I", length) + data + struct.pack(">I", checksum)

        with open(self.path, "ab") as f:
            f.write(record)
            f.flush()
            os.fsync(f.fileno())  # CRITICAL for durability

    def replay(self):
        """
        Read all valid records.
        Stop at first corruption.
        """
        records = []

        with open(self.path, "rb") as f:
            while True:
                # Read length
                len_bytes = f.read(4)
                if not len_bytes:
                    break

                if len(len_bytes) < 4:
                    break  # incomplete

                length = struct.unpack(">I", len_bytes)[0]

                # Read data
                data = f.read(length)
                if len(data) < length:
                    break  # incomplete

                # Read checksum
                checksum_bytes = f.read(4)
                if len(checksum_bytes) < 4:
                    break

                checksum = struct.unpack(">I", checksum_bytes)[0]

                # Validate
                if zlib.crc32(data) != checksum:
                    print("❌ Corruption detected. Stopping replay.")
                    break

                records.append(data)

        return records