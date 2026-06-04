from opecore.core.node_service import NodeService


class BulkService:

    def __init__(self, conn):
        self.conn = conn
        self.node_service = NodeService(conn)

    def execute(self, user, operations):

        results = []

        with self.conn.transaction():

            for op in operations:

                op_type = op["type"]

                # -------------------------
                # CREATE NODE
                # -------------------------
                if op_type == "create":

                    node_id = self.node_service.create_node(
                        op["class_id"],
                        op["attrs"],
                        user
                    )

                    results.append({
                        "type": "create",
                        "node_id": node_id
                    })

                # -------------------------
                # UPDATE NODE
                # -------------------------
                elif op_type == "update":

                    version = self.node_service.update_node(
                        op["node_id"],
                        user,
                        op["base_version"],
                        op["changes"]
                    )

                    results.append({
                        "type": "update",
                        "node_id": op["node_id"],
                        "version": version
                    })

                # -------------------------
                # DELETE NODE
                # -------------------------
                elif op_type == "delete_node":

                    version = self.node_service.delete_node(
                        op["node_id"],
                        user,
                        op["base_version"]
                    )

                    results.append({
                        "type": "delete_node",
                        "node_id": op["node_id"],
                        "version": version
                    })

                # -------------------------
                # DELETE ATTRIBUTE
                # -------------------------
                elif op_type == "delete_attr":

                    version = self.node_service.delete_attr(
                        op["node_id"],
                        user,
                        op["base_version"],
                        op["attr_id"]
                    )

                    results.append({
                        "type": "delete_attr",
                        "node_id": op["node_id"],
                        "version": version
                    })

                else:
                    raise Exception(f"Unknown operation: {op_type}")

        return results