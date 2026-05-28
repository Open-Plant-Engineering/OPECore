import os
import json
from opecore.storage.safe import safe_rename
import uuid


class WALQueue:
    def __init__(self, wal_dir):
        self.wal_dir = wal_dir
        os.makedirs(wal_dir, exist_ok=True)

    # ✅ user creates work file
    def create_work(self):
        wid = str(uuid.uuid4())
        path = os.path.join(self.wal_dir, f"{wid}.work")

        with open(path, "w") as f:
            json.dump({}, f)

        return path

    # ✅ user submits (work → req)
    def submit(self, work_file, payload):
        with open(work_file, "w") as f:
            json.dump(payload, f)

        req_file = work_file.replace(".work", ".req")
        safe_rename(work_file, req_file)

        return req_file

    # ✅ leader sees requests
    def list_requests(self):
        return [
            f for f in os.listdir(self.wal_dir)
            if f.endswith(".req")
        ]

    def mark_processing(self, filename):
        src = os.path.join(self.wal_dir, filename)
        dst = src.replace(".req", ".processing")
        safe_rename(src, dst)
        return dst

    def mark_done(self, filepath):
        dst = filepath.replace(".processing", ".done")
        safe_rename(filepath, dst)

    def mark_failed(self, filepath):
        dst = filepath.replace(".processing", ".failed")
        safe_rename(filepath, dst)
