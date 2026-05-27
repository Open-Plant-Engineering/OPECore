import struct
import zlib

HEADER_FORMAT = "<8sQQLI"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

MAGIC = b"OPECORE1"


class Header:
    def __init__(self, root_offset=0, version=1, txn_id=0):
        self.root_offset = root_offset
        self.version = version
        self.txn_id = txn_id

    def encode(self):
        data = struct.pack(
            "<8sQQL",
            MAGIC,
            self.root_offset,
            self.version,
            self.txn_id,
        )
        crc = zlib.crc32(data)
        return data + struct.pack("<I", crc)

    @staticmethod
    def decode(data: bytes):
        raw = data[:-4]
        crc_stored = struct.unpack("<I", data[-4:])[0]

        if zlib.crc32(raw) != crc_stored:
            return None

        magic, root_offset, version, txn_id = struct.unpack("<8sQQL", raw)

        if magic != MAGIC:
            return None

        return Header(root_offset, version, txn_id)
