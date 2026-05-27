import struct
import hashlib


def encode_object(
    *,
    object_id: int,
    parent_id: int | None,
    fields: list,
    timestamp: int,
    node_id: int,
):
    fields = sorted(fields, key=lambda x: x[0])

    buf = bytearray()

    buf.extend(object_id.to_bytes(16, "little"))

    if parent_id:
        buf.extend(parent_id.to_bytes(16, "little"))
    else:
        buf.extend(b"\x00" * 16)

    buf.extend(b"\x00" * 32)  # placeholder hash

    buf.append(1)
    buf.append(0)

    buf.extend(struct.pack("<Q", timestamp))
    buf.extend(struct.pack("<Q", node_id))

    buf.extend(len(fields).to_bytes(4, "little"))

    for key, typ, value in fields:
        buf.extend(key)
        buf.append(typ)
        buf.extend(value)

    # compute hash excluding hash region
    hash_input = buf[:32] + buf[64:]
    obj_hash = hashlib.sha256(hash_input).digest()

    buf[32:64] = obj_hash

    return bytes(buf), obj_hash