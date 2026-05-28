import json


class StateEngine:
    def __init__(self):
        self.state = {}

    def apply(self, record: bytes):
        """
        Apply one log record to state
        """
        data = json.loads(record.decode())

        op = data.get("op")
        path = data.get("path")

        if op == "SET":
            self.state[path] = data.get("value")

        elif op == "DELETE":
            if path in self.state:
                del self.state[path]

    def rebuild(self, records):
        """
        Rebuild full state from log
        """
        self.state = {}

        for r in records:
            self.apply(r)

    def get(self, path: str):
        return self.state.get(path)

    def list_paths(self):
        return list(self.state.keys())

    def snapshot(self):
        return dict(self.state)
