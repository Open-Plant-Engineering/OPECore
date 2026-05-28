from opecore.state.state import StateEngine


class StateStore:
    def __init__(self, log):
        self.log = log
        self.engine = StateEngine()
        self.loaded = False

    def load(self):
        """
        Load state from log ONCE
        """
        records = self.log.replay()
        self.engine.rebuild(records)
        self.loaded = True

    def ensure_loaded(self):
        if not self.loaded:
            self.load()

    # ✅ LIVE UPDATE
    def apply_record(self, record: bytes):
        """
        Apply new log entry in real-time
        """
        self.engine.apply(record)

    # ✅ API methods
    def get(self, path):
        self.ensure_loaded()
        return self.engine.get(path)

    def exists(self, path):
        self.ensure_loaded()
        return self.engine.exists(path)

    def list(self):
        self.ensure_loaded()
        return self.engine.list_paths()

    def list_children(self, path):
        self.ensure_loaded()
        return self.engine.list_children(path)

    def list_subtree(self, path):
        self.ensure_loaded()
        return self.engine.list_subtree(path)