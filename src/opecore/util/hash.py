import hashlib


def make_sec_key(field: str, value: bytes) -> int:
    h = hashlib.sha256(field.encode() + value).digest()
    return int.from_bytes(h[:16], "little")
