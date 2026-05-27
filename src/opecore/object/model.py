import struct


def decode_object(data: bytes):
    offset = 0

    object_id = int.from_bytes(data[offset:offset+16], "little")
    offset += 16

    parent_id = int.from_bytes(data[offset:offset+16], "little")
    offset += 16

    obj_hash = data[offset:offset+32]
    offset += 32

    version = data[offset]
    offset += 1

    flags = data[offset]
    offset += 1

    timestamp = struct.unpack("<Q", data[offset:offset+8])[0]
    offset += 8

    node_id = struct.unpack("<Q", data[offset:offset+8])[0]
    offset += 8

    field_count = int.from_bytes(data[offset:offset+4], "little")
    offset += 4

    fields = []

    for _ in range(field_count):
        key = data[offset:offset+32]
        offset += 32

        typ = data[offset]
        offset += 1

        value = data[offset:offset+32]
        offset += 32

        fields.append((key, typ, value))

    return {
        "object_id": object_id,
        "parent_id": parent_id,
        "hash": obj_hash,
        "timestamp": timestamp,
        "node_id": node_id,
        "fields": fields,
    }