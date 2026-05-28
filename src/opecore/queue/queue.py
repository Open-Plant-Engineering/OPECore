import os
import json
import uuid

from opecore.storage.safe import safe_rename


class RequestQueue:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(self.path, exist_ok=True)

    def submit(self, payload: dict) -> str:
        """
        Create a new request file
        """
        req_id = str(uuid.uuid4())
        file_path = os.path.join(self.path, f"{req_id}.req")

        with open(file_path, "w") as f:
            json.dump(payload, f)

        return req_id

    def list_requests(self):
        """
        List all pending requests
        """
        return [f for f in os.listdir(self.path) if f.endswith(".req")]

    def mark_processing(self, filename: str) -> str:
        """
        Move file → processing state
        """
        src = os.path.join(self.path, filename)
        dst = src.replace(".req", ".processing")

        ok = safe_rename(src, dst)
        if not ok:
            raise RuntimeError("Failed to claim request")

        return dst

    def mark_done(self, filepath: str):
        """
        processing → done
        """
        dst = filepath.replace(".processing", ".done")
        safe_rename(filepath, dst)

    def mark_failed(self, filepath: str):
        """
        processing → failed
        """
        dst = filepath.replace(".processing", ".failed")
        safe_rename(filepath, dst)