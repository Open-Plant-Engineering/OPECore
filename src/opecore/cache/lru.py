from collections import OrderedDict


class LRUCache:
    def __init__(self, capacity=10000):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return None

        value = self.cache.pop(key)
        self.cache[key] = value  # move to end (most recent)

        return value

    def put(self, key, value):
        if key in self.cache:
            self.cache.pop(key)

        self.cache[key] = value

        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)  # evict LRU