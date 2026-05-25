class IndexEngine:
    def __init__(self):
        self.index = {}

    def update(self, object_id, old_obj, new_obj):
        old_obj = old_obj or {}

        for key, old_value in old_obj.items():
            if key not in new_obj or new_obj[key] != old_value:
                self._remove(object_id, key, old_value)

        for key, new_value in new_obj.items():
            if key not in old_obj or old_obj[key] != new_value:
                self._add(object_id, key, new_value)

    def _add(self, object_id, key, value):
        if key not in self.index:
            self.index[key] = {}
        if value not in self.index[key]:
            self.index[key][value] = set()
        self.index[key][value].add(object_id)

    def _remove(self, object_id, key, value):
        if key in self.index and value in self.index[key]:
            self.index[key][value].discard(object_id)
            if not self.index[key][value]:
                del self.index[key][value]
        if key in self.index and not self.index[key]:
            del self.index[key]

    def query(self, key, value):
        return self.index.get(key, {}).get(value, set())
