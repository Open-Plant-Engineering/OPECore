class QueryEngine:
    def __init__(self, db):
        self.db = db

    def filter(self, conditions: dict):
        """
        conditions = {
            "name": "a",
            "value": 10
        }

        Returns nodes matching ALL conditions (AND)
        """

        result = []

        nodes = self.db.list_nodes()

        for node in nodes:
            if self._match(node, conditions):
                result.append(node)

        return result

    def _match(self, node, conditions):
        for k, v in conditions.items():
            node_value = node.attributes.get(k)

            if node_value != v:
                return False

        return True
