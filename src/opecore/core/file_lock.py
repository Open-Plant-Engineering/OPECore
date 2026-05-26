import os


class FileLock:
    """
    Cross-process atomic file lock.

    Uses atomic file creation (open(..., "x"))
    to guarantee only one writer.
    """

    def __init__(self, path: str):
        self.path = path

    def acquire(self, owner: str, txn_id: str) -> bool:
        try:
            with open(self.path, "x") as f:
                f.write(f"{owner}:{txn_id}")
            return True
        except FileExistsError:
            return False

    def release(self, owner: str, txn_id: str):
        if not os.path.exists(self.path):
            return

        try:
            with open(self.path, "r") as f:
                content = f.read()

            if content != f"{owner}:{txn_id}":
                return  # not owner → ignore

            os.remove(self.path)

        except Exception:
            pass