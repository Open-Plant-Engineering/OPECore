import uuid


class Node:
    def __init__(self, attributes: dict = None, refno: str = None):
        self.refno = refno or self._generate_ref()

        # ✅ everything is attribute
        self.attributes = attributes.copy() if attributes else {}

        # ensure identity exists
        self.attributes["refno"] = self.refno

    def _generate_ref(self):
        return str(uuid.uuid4())

    def to_dict(self):
        # ✅ EXACTLY what you wanted
        return self.attributes

    @staticmethod
    def from_dict(data: dict):
        refno = data.get("refno")
        return Node(attributes=data, refno=refno)