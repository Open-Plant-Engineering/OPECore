class QueryEngine:
    def __init__(self, db):
        self.db = db

    def filter_equal(self, attr_name: str, value):
        """
        Return nodes where attr_name == value
        """

        result = []

        nodes = self.db.list_nodes()

        for node in nodes:
            node_value = node.attributes.get(attr_name)

            if node_value == value:
                result.append(node)

        return result