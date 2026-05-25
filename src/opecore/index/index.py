from typing import Dict, Set, Any


class IndexEngine:
    """
    In-memory attribute index.

    Structure:
        {
            attribute: {
                value: set(object_ids)
            }
        }
    """

    def __init__(self):
        self.index: Dict[str, Dict[Any, Set[int]]] = {}

    # ✅ ===============================
    # UPDATE INDEX (PRIMARY METHOD)
    # ✅ ===============================

    def update(self, object_id: int, old_obj: dict, new_obj: dict):
        """
        Update index based on object changes.

        - Removes stale values
        - Adds new values
        """

        old_obj = old_obj or {}

        # ✅ REMOVE OLD VALUES
        for key, old_value in old_obj.items():
            if key not in new_obj or new_obj[key] != old_value:
                self._remove(object_id, key, old_value)

        # ✅ ADD NEW VALUES
        for key, new_value in new_obj.items():
            if key not in old_obj or old_obj[key] != new_value:
                self._add(object_id, key, new_value)

    # ✅ ===============================
    # INTERNAL OPERATIONS
    # ✅ ===============================

    def _add(self, object_id: int, key: str, value):
        """Add object_id to index[key][value]."""
        if key not in self.index:
            self.index[key] = {}

        if value not in self.index[key]:
            self.index[key][value] = set()

        self.index[key][value].add(object_id)

    def _remove(self, object_id: int, key: str, value):
        """Remove object_id from index[key][value] safely."""

        value_map = self.index.get(key)
        if not value_map:
            return

        obj_set = value_map.get(value)
        if not obj_set:
            return

        obj_set.discard(object_id)

        # ✅ cleanup empty value bucket
        if not obj_set:
            del value_map[value]

        # ✅ cleanup empty key bucket
        if not value_map:
            del self.index[key]

    # ✅ ===============================
    # QUERY
    # ✅ ===============================

    def query(self, key: str, value) -> Set[int]:
        """
        Return set of object_ids matching key=value.
        """
        return self.index.get(key, {}).get(value, set())

    # ✅ ===============================
    # DEBUG / INSPECTION
    # ✅ ===============================

    def dump(self) -> Dict[str, Dict[Any, Set[int]]]:
        """
        Return entire index (for debugging/testing).
        """
        return self.index
