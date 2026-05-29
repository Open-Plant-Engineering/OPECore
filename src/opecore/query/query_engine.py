class QueryEngine:
    def __init__(self, db):
        self.db = db

    def filter(self, query: dict):
        result = []

        nodes = self.db.list_nodes()

        for node in nodes:
            if self._evaluate(node, query):
                result.append(node)

        return result

    def _evaluate(self, node, query):
        # ✅ OR condition
        if "or" in query:
            for sub in query["or"]:
                if self._evaluate(node, sub):
                    return True
            return False

        # ✅ AND condition
        if "and" in query:
            for sub in query["and"]:
                if not self._evaluate(node, sub):
                    return False
            return True

        # ✅ simple condition (base case)
        return self._match_simple(node, query)

    def _match_simple(self, node, conditions):
        for k, v in conditions.items():
            node_value = node.attributes.get(k)

            if node_value != v:
                return False

        return True