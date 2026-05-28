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

    def list(self):
        return self.engine.list_paths()