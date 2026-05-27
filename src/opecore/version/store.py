import time


class VersionStore:
    def __init__(self):
        self.versions = {}  # version_id → metadata
        self.latest = {}    # node_id → version_id

        self._counter = 1

    def create(self, node_id, parent_version=None):
        vid = self._counter
        self._counter += 1

        self.versions[vid] = {
            "node_id": node_id,
            "parent": parent_version,
            "timestamp": int(time.time() * 1000),
        }

        self.latest[node_id] = vid

        return vid

    def get_latest(self, node_id):
        return self.latest.get(node_id)

    def get(self, version_id):
        return self.versions.get(version_id)