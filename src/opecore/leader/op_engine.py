import json
from opecore.model.node import Node

class OPEngine:
    def __init__(self, queue, db):
        self.queue = queue
        self.db = db

    def process_once(self):
        files = self.queue.list_requests()

        for fname in files:
            try:
                path = self.queue.mark_processing(fname)

                with open(path, "r") as f:
                    req = json.load(f)

                ok = self.handle(req)

                if ok:
                    self.queue.mark_done(path)
                else:
                    self.queue.mark_failed(path)

            except Exception as e:
                print("Worker error:", e)

    def handle(self, req):
        action = req.get("action")

        # ✅ CREATE NODE
        if action == "create":
            attrs = req.copy()
            attrs.pop("action", None)

            node = Node(attributes=attrs)

            self.db.create_node(node)
            return True

        # ✅ UPDATE NODE
        if action == "update":
            node = self.db.get_node(req["refno"])
            if not node:
                return False

            updates = req.copy()
            updates.pop("action", None)
            updates.pop("refno", None)

            node.attributes.update(updates)

            self.db.update_node(node)
            return True

        # ✅ DELETE NODE
        if action == "delete":
            self.db.delete_node(req["refno"])
            return True

        return False
