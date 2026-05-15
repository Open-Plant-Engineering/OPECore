class IndexEngine:
    def __init__(self):
        self.index = {}

    def add(self, object_id, data: dict):
        for key, value in data.items():
            if key not in self.index:
                self.index[key] = {}

            if value not in self.index[key]:
                self.index[key][value] = set()

            self.index[key][value].add(object_id)

    def query(self, key, value):
        return list(self.index.get(key, {}).get(value, []))
