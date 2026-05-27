from opecore.storage.log import FileManager
from opecore.index.page import BTreePage
from opecore.index.serialize import serialize_page, deserialize_page

INDEX_PAGE = 5
MAX_KEYS = 4


class BTree:
    def __init__(self, fm: FileManager):
        self.fm = fm
        self.root_offset = None

    def _write(self, page: BTreePage):
        return self.fm.append_record(INDEX_PAGE, serialize_page(page))

    def _read(self, offset):
        _, payload = self.fm.read_at(offset)
        return deserialize_page(payload)

    # 🔍 SEARCH (correct)
    def search(self, key, offset=None):
        if offset is None:
            offset = self.root_offset

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

    # 🚀 INSERT (correct entry point)
    def insert(self, key, value):
        if self.root_offset is None:
            leaf = BTreePage(True)
            leaf.keys = [key]
            leaf.values = [value]

            self.root_offset = self._write(leaf)
            return

        new_offset, promoted_key, right_offset = self._insert(self.root_offset, key, value)

        # root split
        if promoted_key is not None:
            root = BTreePage(False)
            root.keys = [promoted_key]
            root.children = [new_offset, right_offset]

            self.root_offset = self._write(root)
        else:
            self.root_offset = new_offset

    # 🔁 recursive insert
    def _insert(self, offset, key, value):
        page = self._read(offset)

        if page.is_leaf:
            return self._insert_leaf(page, key, value)

        return self._insert_internal(page, key, value)

    # 🌿 LEAF INSERT
    def _insert_leaf(self, page, key, value):
        i = 0
        while i < len(page.keys) and page.keys[i] < key:
            i += 1

        page.keys.insert(i, key)
        page.values.insert(i, value)

        # no split
        if len(page.keys) <= MAX_KEYS:
            return self._write(page), None, None

        # split
        mid = len(page.keys) // 2

        left = BTreePage(True)
        right = BTreePage(True)

        left.keys = page.keys[:mid]
        left.values = page.values[:mid]

        right.keys = page.keys[mid:]
        right.values = page.values[mid:]

        left_offset = self._write(left)
        right_offset = self._write(right)

        promoted_key = right.keys[0]

        return left_offset, promoted_key, right_offset

    # 🌿 INTERNAL INSERT
    def _insert_internal(self, page, key, value):
        i = 0
        while i < len(page.keys) and key >= page.keys[i]:
            i += 1

        child_offset = page.children[i]

        new_child_offset, promoted_key, right_offset = self._insert(child_offset, key, value)

        # no split from child
        if promoted_key is None:
            page.children[i] = new_child_offset
            return self._write(page), None, None

        # child split → insert into this page
        page.keys.insert(i, promoted_key)
        page.children[i] = new_child_offset
        page.children.insert(i + 1, right_offset)

        # no split needed
        if len(page.keys) <= MAX_KEYS:
            return self._write(page), None, None

        # split internal page
        mid = len(page.keys) // 2

        left = BTreePage(False)
        right = BTreePage(False)

        left.keys = page.keys[:mid]
        right.keys = page.keys[mid+1:]

        left.children = page.children[:mid+1]
        right.children = page.children[mid+1:]

        promoted = page.keys[mid]

        left_offset = self._write(left)
        right_offset = self._write(right)

        return left_offset, promoted, right_offset