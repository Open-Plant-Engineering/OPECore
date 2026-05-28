import os
import time


def safe_write(path: str, data: bytes, retries=5):
    """
    Write file safely:
    write -> temp -> rename
    """
    temp_path = path + ".tmp"

    for attempt in range(retries):
        try:
            # Write temp file
            with open(temp_path, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())

            # Atomic replace
            os.replace(temp_path, path)
            return True

        except Exception:
            time.sleep(0.05)

    return False


def safe_rename(src: str, dst: str, retries=5):
    """
    Retry-safe rename
    """
    for _ in range(retries):
        try:
            os.replace(src, dst)
            return True
        except Exception:
            time.sleep(0.05)

    return False


def safe_delete(path: str, retries=5):
    """
    Safe delete (idempotent)
    """
    for _ in range(retries):
        try:
            if os.path.exists(path):
                os.remove(path)
            return True
        except Exception:
            time.sleep(0.05)

    return False