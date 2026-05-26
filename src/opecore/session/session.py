import time
from typing import Optional, List, Dict

from opecore.core.engine import Engine


class Session:
    """
    Represents a user session with snapshot isolation.
    """

    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_time = time.time()

    # ✅ ===============================
    # READ (snapshot-consistent)
    # ✅ ===============================

    def read(self, object_id: int) -> Optional[Dict]:
        return self.engine.read_as_of(object_id, self.session_time)

    def read_many(self, object_ids: List[int]) -> Dict[int, Dict]:
        result = {}

        for obj_id in object_ids:
            data = self.read(obj_id)
            if data is not None:
                result[obj_id] = data

        return result

    def query(self, key: str, value) -> List[int]:
        """
        Returns object IDs.
        Use read() for snapshot values.
        """
        return self.engine.query(key, value)

    def query_and_read(self, filters: dict) -> Dict[int, Dict]:
        """
        Combined helper:
        query + snapshot read
        """
        ids = self.engine.query_multiple(filters)
        return self.read_many(list(ids))

    # ✅ ===============================
    # WRITE (always latest)
    # ✅ ===============================

    def update(self, object_id: int, attribute: str, value, owner: str):
        self.engine.update_attribute(object_id, attribute, value, owner)

    # ✅ ===============================
    # SESSION CONTROL
    # ✅ ===============================

    def refresh(self):
        """
        Move session to latest state.
        """
        self.session_time = time.time()