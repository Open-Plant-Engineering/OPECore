from typing import Dict, Set, Any


class IndexEngine:
    def __init__(self):
        self.index: Dict[str, Dict[Any, Set[int]]] = {}

    # ✅ ===============================
    # UPDATE INDEX
    # ✅ ===============================

    def update(self, object_id: int, old_obj: dict, new_obj: dict):
        old_obj = old_obj or {}

        # ✅ REMOVE OLD VALUES
        for key, old_value in old_obj.items():
            if key.startswith("__"):
                continue

            if key not in new_obj or new_obj[key] != old_value:
                self._remove(object_id, key, old_value)

        # ✅ ADD NEW VALUES
        for key, new_value in new_obj.items():
            if key.startswith("__"):
                continue

            if new_value is None:
                continue

            if key not in old_obj or old_obj.get(key) != new_value:
                self._add(object_id, key, new_value)

    # ✅ ===============================
    # INTERNAL
    # ✅ ===============================

    def _add(self, object_id: int, key: str, value):
        if key not in self.index:
            self.index[key] = {}

        if value not in self.index[key]:
            self.index[key][value] = set()

        self.index[key][value].add(object_id)

    def _remove(self, object_id: int, key: str, value):
        value_map = self.index.get(key)
        if not value_map:
            return

        obj_set = value_map.get(value)
        if not obj_set:
            return

        obj_set.discard(object_id)

        if not obj_set:
            del value_map[value]

        if not value_map:
            del self.index[key]

    # ✅ ===============================
    # QUERY
    # ✅ ===============================

    def query(self, key: str, value) -> Set[int]:
        return self.index.get(key, {}).get(value, set())

    # ✅ ===============================
    # UTIL
    # ✅ ===============================

    def get_all_objects(self):
        result = set()

        for value_map in self.index.values():
            for obj_set in value_map.values():
                result.update(obj_set)

        return result

    def dump(self) -> Dict[str, Dict[Any, Set[int]]]:
        return self.index