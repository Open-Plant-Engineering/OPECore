import struct
import pickle
from opecore.index.page import BTreePage

LEAF = 1
INTERNAL = 2


def serialize_page(page: BTreePage) -> bytes:
    buf = bytearray()

    if page.is_leaf:
        buf.append(LEAF)
    else:
        buf.append(INTERNAL)

    buf.extend(len(page.keys).to_bytes(4, "little"))

    for key in page.keys:
        buf.extend(key.to_bytes(16, "little"))  # snowflake ids

    if page.is_leaf:
        for val in page.values:
            data = pickle.dumps(val)
            buf.extend(len(data).to_bytes(4, "little"))
            buf.extend(data)

    else:
        for child in page.children:
            buf.extend(child.to_bytes(8, "little"))  # offset

    return bytes(buf)


def deserialize_page(data: bytes) -> BTreePage:
    offset = 0

    typ = data[offset]
    offset += 1

    is_leaf = typ == LEAF

    count = int.from_bytes(data[offset:offset+4], "little")
    offset += 4

    page = BTreePage(is_leaf)

    for _ in range(count):
        key = int.from_bytes(data[offset:offset+16], "little")
        offset += 16
        page.keys.append(key)

    if is_leaf:
        for _ in range(count):
            size = int.from_bytes(data[offset:offset+4], "little")
            offset += 4
            
            val = pickle.loads(data[offset:offset+size])
            offset += size
            page.values.append(val)
    else:
        for _ in range(count + 1):
            child = int.from_bytes(data[offset:offset+8], "little")
            offset += 8
            page.children.append(child)

    return page