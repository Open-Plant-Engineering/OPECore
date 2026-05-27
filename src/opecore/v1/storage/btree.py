BTREE_RECORD = 5
MAX_KEYS = 4


class BTreePage:
    def __init__(self, is_leaf):
        self.is_leaf = is_leaf
        self.keys = []
        self.values = []
        self.children = []


class BTree:
    """
    SOLID v1 BTree

    Responsibility:
    - Index key → value mapping
    - Support search, insert, range queries
    """

    def __init__(self, file_manager):
        self.fm = file_manager
        self.root_offset = None

        # in-memory page cache
        self.cache = {}

    # ------------------------
    # PUBLIC API
    # ------------------------

    def search(self, key, offset=None):
        if offset is None:
            offset = self.root_offset

        if offset is None:
            return None

        page = self._read(offset)

        if page.is_leaf:
            for i, k in enumerate(page.keys):
                if k == key:
                    return page.values[i]
            return None

        i = 0
        while i < len(page.keys) and key >= page.keys[i]:
            i += 1

        return self.search(key, page.children[i])

    def insert(self, key, value, txn_id):
        if self.root_offset is None:
            leaf = BTreePage(True)
            leaf.keys = [key]
            leaf.values = [value]

            self.root_offset = self._write(leaf, txn_id)
            return

        new_root, promoted, right = self._insert(self.root_offset, key, value, txn_id)

        if promoted is not None:
            root = BTreePage(False)
            root.keys = [promoted]
            root.children = [new_root, right]

            self.root_offset = self._write(root, txn_id)
        else:
            self.root_offset = new_root

    def range(self, start, end):
        return self._range(self.root_offset, start, end, [])

    # ------------------------
    # INTERNAL
    # ------------------------

    def _insert(self, offset, key, value, txn_id):
        page = self._read(offset)

        if page.is_leaf:
            return self._insert_leaf(page, key, value, txn_id)

        i = 0
        while i < len(page.keys) and key >= page.keys[i]:
            i += 1

        child = page.children[i]

        new_child, promoted, right = self._insert(child, key, value, txn_id)

        if promoted is None:
            page.children[i] = new_child
            return self._write(page, txn_id), None, None

        page.keys.insert(i, promoted)
        page.children[i] = new_child
        page.children.insert(i + 1, right)

        if len(page.keys) <= MAX_KEYS:
            return self._write(page, txn_id), None, None

        return self._split_internal(page, txn_id)

    def _insert_leaf(self, page, key, value, txn_id):
        i = 0
        while i < len(page.keys) and page.keys[i] < key:
            i += 1

        page.keys.insert(i, key)
        page.values.insert(i, value)

        if len(page.keys) <= MAX_KEYS:
            return self._write(page, txn_id), None, None

        return self._split_leaf(page, txn_id)

    def _split_leaf(self, page, txn_id):
        mid = len(page.keys) // 2

        left = BTreePage(True)
        right = BTreePage(True)

        left.keys = page.keys[:mid]
        left.values = page.values[:mid]

        right.keys = page.keys[mid:]
        right.values = page.values[mid:]

        left_offset = self._write(left, txn_id)
        right_offset = self._write(right, txn_id)

        return left_offset, right.keys[0], right_offset

    def _split_internal(self, page, txn_id):
        mid = len(page.keys) // 2

        left = BTreePage(False)
        right = BTreePage(False)

        left.keys = page.keys[:mid]
        right.keys = page.keys[mid + 1:]

        left.children = page.children[:mid + 1]
        right.children = page.children[mid + 1:]

        promoted = page.keys[mid]

        left_offset = self._write(left, txn_id)
        right_offset = self._write(right, txn_id)

        return left_offset, promoted, right_offset

    def _range(self, offset, start, end, result):
        if offset is None:
            return result

        page = self._read(offset)

        if page.is_leaf:
            for k, v in zip(page.keys, page.values):
                if start <= k <= end:
                    result.append(v)
            return result

        for child in page.children:
            self._range(child, start, end, result)

        return result

    def _write(self, page, txn_id):
        data = self._serialize(page)

        offset = self.fm.append_txn_record(
            BTREE_RECORD,
            txn_id,
            data
        )

        self.cache[offset] = page
        return offset

    def _read(self, offset):
        if offset in self.cache:
            return self.cache[offset]

        _, _, payload = self.fm.read_txn_record(offset)

        page = self._deserialize(payload)

        self.cache[offset] = page
        return page

    # ------------------------
    # SERIALIZATION
    # ------------------------

    def _serialize(self, page):
        data = b""
        data += (1 if page.is_leaf else 0).to_bytes(1, "little")
        data += len(page.keys).to_bytes(4, "little")

        for k in page.keys:
            data += k.to_bytes(8, "little")

        if page.is_leaf:
            for v in page.values:
                data += v.to_bytes(8, "little")
        else:
            data += len(page.children).to_bytes(4, "little")
            for c in page.children:
                data += c.to_bytes(8, "little")

        return data

    def _deserialize(self, data):
        pos = 0

        is_leaf = bool(data[pos])
        pos += 1

        count = int.from_bytes(data[pos:pos+4], "little")
        pos += 4

        keys = []
        for _ in range(count):
            keys.append(int.from_bytes(data[pos:pos+8], "little"))
            pos += 8

        page = BTreePage(is_leaf)
        page.keys = keys

        if is_leaf:
            values = []
            for _ in range(count):
                values.append(int.from_bytes(data[pos:pos+8], "little"))
                pos += 8
            page.values = values
        else:
            ccount = int.from_bytes(data[pos:pos+4], "little")
            pos += 4

            children = []
            for _ in range(ccount):
                children.append(int.from_bytes(data[pos:pos+8], "little"))
                pos += 8

            page.children = children

        return page
