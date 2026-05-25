from typing import Dict, Set, Any


class IndexEngine:
    """
    In-memory index engine.

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
    # ADD / UPDATE INDEX
    # ✅ ===============================

    def add(self, object_id: int, obj: dict):
        """
        Index all attributes of an object.
        """
        for key, value in obj.items():
            # ensure key exists
            if key not in self.index:
                self.index[key] = {}

            # ensure value bucket exists
            if value not in self.index[key]:
                self.index[key][value] = set()

            # add object reference
            self.index[key][value].add(object_id)

    # ✅ ===============================
    # QUERY
    # ✅ ===============================

    def query(self, key: str, value) -> Set[int]:
        return self.index.get(key, {}).get(value, set())

    # ✅ ===============================
    # DEBUG / INSPECTION
    # ✅ ===============================

    def dump(self) -> Dict:
        return self.index
