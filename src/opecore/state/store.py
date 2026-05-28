from opecore.state.state import StateEngine

class StateStore:
    def __init__(self, log):
        self.log = log
        self.engine = StateEngine()

    def load(self):
        records = self.log.replay()
        self.engine.rebuild(records)

    def get(self, path):
        return self.engine.get(path)

    def exists(self, path):
        return self.engine.exists(path)

    def list(self):
        return self.engine.list_paths()

    def list_children(self, path):
        return self.engine.list_children(path)

    def list_subtree(self, path):
        return self.engine.list_subtree(path)