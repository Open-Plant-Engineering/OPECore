import struct
import zlib

RECORD_HEADER = "<I B I"
RECORD_HEADER_SIZE = struct.calcsize(RECORD_HEADER)

MAGIC = 0xABCD1234

class Record:

    @staticmethod
    def encode(rtype: int, payload: bytes) -> bytes:
        header = struct.pack(RECORD_HEADER, MAGIC, rtype, len(payload))
        crc = zlib.crc32(header + payload)
        return header + payload + struct.pack("<I", crc)

    @staticmethod
    def decode(f):
        header = f.read(RECORD_HEADER_SIZE)
        if not header:
            return None

        magic, rtype, size = struct.unpack(RECORD_HEADER, header)
        if magic != MAGIC:
            raise ValueError("Invalid record magic")

        payload = f.read(size)
        crc_read = struct.unpack("<I", f.read(4))[0]

        if zlib.crc32(header + payload) != crc_read:
            raise ValueError("CRC mismatch")

        return rtype, payload
