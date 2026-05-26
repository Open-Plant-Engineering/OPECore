import time
import threading
import socket
import getpass


class SnowflakeIDGenerator:
    def __init__(self, machine_id: int = None):
        self.machine_id = machine_id or self._generate_machine_id()
        self.sequence = 0
        self.last_timestamp = -1
        self.lock = threading.Lock()

        self.machine_bits = 10
        self.sequence_bits = 12

        self.max_sequence = (1 << self.sequence_bits) - 1

        self.machine_shift = self.sequence_bits
        self.timestamp_shift = self.sequence_bits + self.machine_bits

    def _generate_machine_id(self):
        name = socket.gethostname() + getpass.getuser()
        return abs(hash(name)) % 1024

    def _current_millis(self):
        return int(time.time() * 1000)

    def generate(self):
        with self.lock:
            ts = self._current_millis()

            if ts == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.max_sequence
                if self.sequence == 0:
                    while ts <= self.last_timestamp:
                        ts = self._current_millis()
            else:
                self.sequence = 0

            self.last_timestamp = ts

            return (
                (ts << self.timestamp_shift) |
                (self.machine_id << self.machine_shift) |
                self.sequence
            )