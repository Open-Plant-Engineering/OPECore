import json


def is_child(parent: str, child: str) -> bool:
    if not child.startswith(parent.rstrip("/") + "/"):
        return False

    # remove parent prefix
    rest = child[len(parent.rstrip("/")) + 1:]

    # direct child = no further "/"
    return "/" not in rest


def is_descendant(parent: str, child: str) -> bool:
    return child.startswith(parent.rstrip("/") + "/")


class StateEngine:
    def __init__(self):
        self.state = {}

    def apply(self, record: bytes):
        data = json.loads(record.decode())

        op = data.get("op")
        path = data.get("path")

        if op == "SET":
            self.state[path] = data.get("value")

        elif op == "DELETE":
            if path in self.state:
                del self.state[path]

    def rebuild(self, records):
        self.state = {}

        for r in records:
            self.apply(r)

    # ✅ basic read
    def get(self, path: str):
        return self.state.get(path)

    def exists(self, path: str) -> bool:
        return path in self.state

    def list_paths(self):
        return list(self.state.keys())

    # ✅ NEW: direct children
    def list_children(self, path: str):
        result = []

        for p in self.state.keys():
            if is_child(path, p):
                result.append(p)

        return result

    # ✅ NEW: subtree
    def list_subtree(self, path: str):
        return [
            p for p in self.state.keys()
            if p == path or is_descendant(path, p)
        ]