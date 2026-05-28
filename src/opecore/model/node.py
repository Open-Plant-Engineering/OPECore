import uuid


class Node:
    def __init__(
        self,
        name: str,
        node_type: str,
        owner: str = None,
        attributes: dict = None,
        refno: str = None,
    ):
        self.refno = refno or self._generate_ref()
        self.name = name
        self.type = node_type
        self.owner = owner
        self.attributes = attributes or {}
        self.lock = None  # future use

    def _generate_ref(self):
        return str(uuid.uuid4())

    def to_dict(self):
        return {
            "refno": self.refno,
            "name": self.name,
            "type": self.type,
            "owner": self.owner,
            "attributes": self.attributes,
            "lock": self.lock,
        }

    @staticmethod
    def from_dict(data: dict):
        node = Node(
            name=data.get("name"),
            node_type=data.get("type"),
            owner=data.get("owner"),
            attributes=data.get("attributes"),
            refno=data.get("refno"),
        )
        node.lock = data.get("lock")
        return node
