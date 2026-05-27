import time
import threading


class SnowflakeIDGenerator:
    """
    SOLID v1 Snowflake ID Generator

    Responsibility:
    - Generate globally unique, time-ordered IDs

    Structure:
    64-bit ID:
    [timestamp | node_id | sequence]
    """

    def __init__(self, node_id: int = 1):
        self.node_id = node_id & 0x3FF  # 10 bits
        self.sequence = 0
        self.last_timestamp = -1

        self.lock = threading.Lock()

    def generate(self) -> int:
        with self.lock:
            timestamp = self._current_time()

            if timestamp == self.last_timestamp:
                self.sequence += 1
                if self.sequence > 0xFFF:  # 12 bits
                    timestamp = self._wait_next(timestamp)
                    self.sequence = 0
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return self._compose_id(timestamp, self.node_id, self.sequence)

    # ------------------------
    # INTERNAL
    # ------------------------

    def _current_time(self):
        return int(time.time() * 1000)

    def _wait_next(self, last_timestamp):
        timestamp = self._current_time()

        while timestamp <= last_timestamp:
            timestamp = self._current_time()

        return timestamp

    def _compose_id(self, ts, node, seq):
        """
        Layout:
        41 bits timestamp
        10 bits node
        12 bits sequence
        """
        return ((ts << 22) | (node << 12) | seq)