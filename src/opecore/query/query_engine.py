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
        for k, condition in conditions.items():
            node_value = node.attributes.get(k)

            # ✅ simple equality
            if not isinstance(condition, dict):
                if node_value != condition:
                    return False
                continue

            # ✅ operator-based condition
            if not self._apply_operator(node_value, condition):
                return False

        return True

    def _apply_operator(self, value, condition: dict):
        for op, expected in condition.items():

            # ✅ equality
            if op == "eq":
                if value != expected:
                    return False

            # ✅ greater than
            elif op == "gt":
                if value <= expected:
                    return False

            # ✅ less than
            elif op == "lt":
                if value >= expected:
                    return False

            # ✅ greater or equal
            elif op == "gte":
                if value < expected:
                    return False

            # ✅ less or equal
            elif op == "lte":
                if value > expected:
                    return False

            # ✅ IN operator
            elif op == "in":
                if value not in expected:
                    return False

            # ✅ wildcard match (very simple)
            elif op == "like":
                if not isinstance(value, str):
                    return False

                pattern = expected.replace("*", "")
                if expected.startswith("*") and expected.endswith("*"):
                    if pattern not in value:
                        return False
                elif expected.startswith("*"):
                    if not value.endswith(pattern):
                        return False
                elif expected.endswith("*"):
                    if not value.startswith(pattern):
                        return False
                else:
                    if value != expected:
                        return False

            else:
                raise ValueError(f"Unknown operator: {op}")

        return True