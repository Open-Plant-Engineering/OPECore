import os
import struct
import hashlib
import zlib

HEADER_FORMAT = "<8sHHQQQQI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

MAGIC = b"MYDBv1\x00\x00"

class FileHeader:
    def __init__(self, root_offset=0, version=1):
        self.root_offset = root_offset
        self.version = version

    def encode(self):
        data = struct.pack(
            "<8sHHQQQQ",
            MAGIC,
            1, 0,                      # version
            0,                         # file_id
            0,                         # ts
            self.root_offset,
            0                          # features
        )
        crc = zlib.crc32(data)
        return data + struct.pack("<I", crc)

    @staticmethod
    def decode(data: bytes):
        base = data[:-4]
        crc_expected = struct.unpack("<I", data[-4:])[0]
        if zlib.crc32(base) != crc_expected:
            raise ValueError("Header CRC mismatch")

        parts = struct.unpack("<8sHHQQQQ", base)
        root_offset = parts[5]
        return FileHeader(root_offset)