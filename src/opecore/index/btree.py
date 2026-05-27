from opecore.storage.log import FileManager
from opecore.index.page import BTreePage
from opecore.index.serialize import serialize_page, deserialize_page
from opecore.cache.lru import LRUCache


INDEX_PAGE = 5
MAX_KEYS = 4


class BTree:
    def __init__(self, fm: FileManager):
        self.fm = fm
        self.root_offset = fm.header.root_offset or None
        self.page_cache = LRUCache(5000)

    def _write(self, page, txn_id):
        data = serialize_page(page)
        offset = self.fm.append_txn_record(INDEX_PAGE, txn_id, data)

        # ✅ cache the new page immediately
        self.page_cache.put(offset, page)

        return offset

    def _read(self, offset):
        cached = self.page_cache.get(offset)
        if cached:
            return cached

        _, _, payload = self.fm.read_txn_record(offset)
        page = deserialize_page(payload)

        self.page_cache.put(offset, page)

        return page

    # 🔍 SEARCH (correct)
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

        assert len(page.children) == len(page.keys) + 1
        return self.search(key, page.children[i])

    # 🚀 INSERT (correct entry point)
    def insert(self, key, value, txn_id):
        if self.root_offset is None:
            leaf = BTreePage(True)
            leaf.keys = [key]
            leaf.values = [value]

            self.root_offset = self._write(leaf, txn_id)

            self.fm.update_root(self.root_offset)
            return

        new_offset, promoted_key, right_offset = self._insert(self.root_offset, key, value, txn_id)

        # root split
        if promoted_key is not None:
            root = BTreePage(False)
            root.keys = [promoted_key]
            root.children = [new_offset, right_offset]

            self.root_offset = self._write(root,txn_id)
        else:
            self.root_offset = new_offset

        self.fm.update_root(self.root_offset)

    # 🔁 recursive insert
    def _insert(self, offset, key, value, txn_id):
        page = self._read(offset)

        if page.is_leaf:
            return self._insert_leaf(page, key, value, txn_id)

        return self._insert_internal(page, key, value, txn_id)

    # 🌿 LEAF INSERT
    def _insert_leaf(self, page, key, value, txn_id):
        i = 0
        while i < len(page.keys) and page.keys[i] < key:
            i += 1

        page.keys.insert(i, key)
        page.values.insert(i, value)

        # no split
        if len(page.keys) <= MAX_KEYS:
            return self._write(page, txn_id), None, None

        # split
        mid = len(page.keys) // 2

        left = BTreePage(True)
        right = BTreePage(True)

        left.keys = page.keys[:mid]
        left.values = page.values[:mid]

        right.keys = page.keys[mid:]
        right.values = page.values[mid:]

        left_offset = self._write(left, txn_id)
        right_offset = self._write(right, txn_id)

        promoted_key = right.keys[0]

        return left_offset, promoted_key, right_offset

    # 🌿 INTERNAL INSERT
    def _insert_internal(self, page, key, value, txn_id):
        i = 0
        while i < len(page.keys) and key >= page.keys[i]:
            i += 1

        child_offset = page.children[i]

        new_child_offset, promoted_key, right_offset = self._insert(child_offset, key, value, txn_id)

        # no split from child
        if promoted_key is None:
            page.children[i] = new_child_offset
            return self._write(page, txn_id), None, None

        # child split → insert into this page
        page.keys.insert(i, promoted_key)
        page.children[i] = new_child_offset
        page.children.insert(i + 1, right_offset)

        # no split needed
        if len(page.keys) <= MAX_KEYS:
            return self._write(page, txn_id), None, None

        # split internal page
        mid = len(page.keys) // 2

        left = BTreePage(False)
        right = BTreePage(False)

        left.keys = page.keys[:mid]
        right.keys = page.keys[mid+1:]

        left.children = page.children[:mid+1]
        right.children = page.children[mid+1:]

        promoted = page.keys[mid]

        left_offset = self._write(left, txn_id)
        right_offset = self._write(right, txn_id)

        return left_offset, promoted, right_offset

    def range(self, start, end, offset=None, results=None):
        if results is None:
            results = []
    
        if offset is None:
            offset = self.root_offset
    
        if offset is None:
            return results
    
        page = self._read(offset)
    
        if page.is_leaf:
            for k, v in zip(page.keys, page.values):
                if start <= k <= end:
                    results.append(v)
            return results
    
        # internal node – traverse relevant children
        i = 0
        while i < len(page.keys) and start >= page.keys[i]:
            i += 1
    
        # traverse from i onward (could overlap multiple ranges)
        for j in range(i, len(page.children)):
            self.range(start, end, page.children[j], results)
    
        return results