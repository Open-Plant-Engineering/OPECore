import hashlib


class SecondaryIndex:
    """
    SOLID Secondary Index

    Responsibility:
    - Map (field, value) → list of object_ids
    """

    def __init__(self, btree):
        self.index = btree
        self._counters = {}

    # ------------------------
    # INSERT
    # ------------------------

    def add(self, field: str, value: bytes, object_id: int, txn_id: int):
        base_key = self._make_key(field, value)

        # ✅ use only 48 bits
        base_key = base_key & ((1 << 48) - 1)

        # ✅ counter per (field,value)
        cnt = self._counters.get(base_key, 0)
        self._counters[base_key] = cnt + 1

        # ✅ compose final key (64-bit safe)
        composite = (base_key << 16) | (cnt & 0xFFFF)

        self.index.insert(composite, object_id, txn_id)

    # ------------------------
    # QUERY
    # ------------------------

    def find(self, field: str, value: bytes):
        base_key = self._make_key(field, value)
        base_key = base_key & ((1 << 48) - 1)

        start = base_key << 16
        end = start | 0xFFFF

        return self.index.range(start, end)

    # ------------------------
    # INTERNAL
    # ------------------------

    def _make_key(self, field: str, value: bytes):
        h = hashlib.sha256()
        h.update(field.encode())
        h.update(b":")
        h.update(value)
        return int.from_bytes(h.digest()[:8], "little")