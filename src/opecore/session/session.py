import time
from typing import Optional, List

from opecore.core.engine import Engine


class Session:
    """
    Represents a user session with snapshot isolation.
    """

    def __init__(self, engine: Engine):
        self.engine = engine
        self.session_time = time.time()

    # ✅ ===============================
    # READ (time-consistent)
    # ✅ ===============================

    def read(self, object_id: int) -> Optional[bytes]:
        return self.engine.read_as_of(object_id, self.session_time)

    def query(self, key: str, value) -> List[int]:
        """
        Query returns object IDs, but read() gives snapshot view.
        """
        return self.engine.query(key, value)

    # ✅ ===============================
    # WRITE (always current)
    # ✅ ===============================

    def update(self, object_id: int, attribute: str, value, owner: str):
        self.engine.update_attribute(object_id, attribute, value, owner)

    # ✅ ===============================
    # REFRESH (very important)
    # ✅ ===============================

    def refresh(self):
        """
        Move session to latest state.
        """
        self.session_time = time.time()
