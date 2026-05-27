import pickle
import os


class SnapshotManager:
    """
    SOLID SnapshotManager

    Responsibility:
    - Save storage state
    - Load storage state
    """

    def __init__(self, path):
        self.path = path + ".snapshot"

    # ------------------------
    # SAVE SNAPSHOT
    # ------------------------

    def save(self, chunk_store, object_store, last_offset):
        data = {
            "chunk_index": chunk_store.index,
            "object_index": object_store.index,
            "last_offset": last_offset
        }

        with open(self.path, "wb") as f:
            pickle.dump(data, f)

    # ------------------------
    # LOAD SNAPSHOT
    # ------------------------

    def load(self):
        if not os.path.exists(self.path):
            return None

        with open(self.path, "rb") as f:
            return pickle.load(f)
