import os


class Config:
    def __init__(self, base_path: str):
        self.base_path = base_path

        # core files
        self.db_file = os.path.join(base_path, "main.db")
        self.claims_file = os.path.join(base_path, "claims.json")
        self.leader_file = os.path.join(base_path, "leader.info")
        self.wal_dir = os.path.join(base_path, "wal")

    def ensure_dirs(self):
        os.makedirs(self.base_path, exist_ok=True)
        os.makedirs(self.wal_dir, exist_ok=True)
