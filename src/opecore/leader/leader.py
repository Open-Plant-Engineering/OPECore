import os
import json
import uuid
import time

from opecore.storage.safe import safe_write


LEADER_TIMEOUT = 5  # seconds


class Leader:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.file = os.path.join(db_path, "leader.info")
        self.session_id = str(uuid.uuid4())

    def try_become_leader(self) -> bool:
        """
        Become leader if:
        - no leader exists
        OR
        - leader is dead (timeout)
        """
        now = time.time()

        if not os.path.exists(self.file):
            return self._write_leader(now)

        # Read existing leader
        try:
            with open(self.file, "r") as f:
                data = json.load(f)
        except Exception:
            # corrupted file → takeover allowed
            return self._write_leader(now)

        leader_id = data.get("leader")
        ts = data.get("ts", 0)

        # ✅ Leader still alive
        if now - ts < LEADER_TIMEOUT:
            return False

        # ✅ Leader expired → attempt takeover
        return self._write_leader(now)

    def _write_leader(self, ts) -> bool:
        """
        Write leader file
        """
        data = {
            "leader": self.session_id,
            "ts": ts
        }

        ok = safe_write(self.file, json.dumps(data).encode())

        if not ok:
            return False

        # ✅ Re-check (important for race)
        return self.is_leader()

    def is_leader(self) -> bool:
        if not os.path.exists(self.file):
            return False

        try:
            with open(self.file, "r") as f:
                data = json.load(f)
        except Exception:
            return False

        return data.get("leader") == self.session_id

    def heartbeat(self):
        """
        Update timestamp → show leader is alive
        """
        if not self.is_leader():
            return False

        data = {
            "leader": self.session_id,
            "ts": time.time()
        }

        return safe_write(self.file, json.dumps(data).encode())
