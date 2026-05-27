import time
import socket
import getpass
import hashlib
import threading


class SnowflakeGenerator:
    def __init__(self, db_id: int):
        self.db_id = db_id & 0xFFFF

        identity = f"{getpass.getuser()}@{socket.gethostname()}"
        self.node_id = int(hashlib.sha256(identity.encode()).hexdigest(), 16) & 0xFFFF

        self.lock = threading.Lock()
        self.last_ts = 0
        self.counter = 0

    def generate(self) -> int:
        with self.lock:
            ts = int(time.time() * 1000)

            if ts == self.last_ts:
                self.counter += 1
            else:
                self.counter = 0
                self.last_ts = ts

            return (
                (ts << 80)
                | (self.node_id << 64)
                | (self.db_id << 48)
                | self.counter
            )

    @staticmethod
    def decode(sid: int):
        return {
            "timestamp": (sid >> 80) & ((1 << 48) - 1),
            "node_id": (sid >> 64) & 0xFFFF,
            "db_id": (sid >> 48) & 0xFFFF,
            "counter": sid & ((1 << 48) - 1),
        }