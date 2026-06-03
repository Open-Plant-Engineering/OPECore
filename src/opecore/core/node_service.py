import uuid
from opecore.core.attr_def import ATTR_TYPES, REQUIRED_ATTRS, Attr
from opecore.core.claim_service import ClaimService
from opecore.models.exceptions import (
    ValidationError, VersionConflictError
)

class NodeService:

    def __init__(self, conn):
        self.conn = conn

    # -------------------------
    # CREATE NODE
    # -------------------------
    def create_node(self, class_id, attrs, user):

        if not REQUIRED_ATTRS.issubset(attrs.keys()):
            raise ValidationError("Missing required attributes")

        node_id = str(uuid.uuid4())

        with self.conn.transaction():
            with self.conn.cursor() as cur:

                cur.execute("""
                INSERT INTO versions(node_id, parent_version, created_by)
                VALUES (%s, NULL, %s)
                RETURNING version_id
                """, (node_id, user))

                version_id = cur.fetchone()["version_id"]

                self._insert_attrs(cur, node_id, version_id, attrs)

                cur.execute("""
                INSERT INTO nodes(node_id, class_id, current_version)
                VALUES (%s, %s, %s)
                """, (node_id, class_id, version_id))

        return node_id

    # -------------------------
    # UPDATE NODE
    # -------------------------
    def update_node(self, node_id, user, base_version, changes):

        with self.conn.transaction():
            with self.conn.cursor() as cur:

                ClaimService.validate(self.conn, node_id, user)

                cur.execute("""
                SELECT current_version FROM nodes WHERE node_id=%s
                """, (node_id,))

                current_version = cur.fetchone()["current_version"]

                if current_version != base_version:
                    raise VersionConflictError("Version mismatch")

                cur.execute("""
                INSERT INTO versions(node_id, parent_version, created_by)
                VALUES (%s, %s, %s)
                RETURNING version_id
                """, (node_id, current_version, user))

                new_version = cur.fetchone()["version_id"]

                self._insert_attrs(cur, node_id, new_version, changes)

                cur.execute("""
                UPDATE nodes SET current_version=%s WHERE node_id=%s
                """, (new_version, node_id))

        return new_version

    # -------------------------
    # DELETE NODE
    # -------------------------
    def delete_node(self, node_id, user, version):
        return self.update_node(node_id, user, version, {
            Attr.DELETED: True
        })

    # -------------------------
    # DELETE ATTRIBUTE
    # -------------------------
    def delete_attr(self, node_id, user, base_version, attr_id):

        with self.conn.transaction():
            with self.conn.cursor() as cur:

                ClaimService.validate(self.conn, node_id, user)

                cur.execute("""
                INSERT INTO versions(node_id, parent_version, created_by)
                VALUES (%s, %s, %s)
                RETURNING version_id
                """, (node_id, base_version, user))

                version = cur.fetchone()["version_id"]

                cur.execute("""
                INSERT INTO attr_deleted VALUES (%s, %s, %s)
                """, (node_id, version, attr_id))

                cur.execute("""
                UPDATE nodes SET current_version=%s WHERE node_id=%s
                """, (version, node_id))

    # -------------------------
    # INSERT ATTRIBUTES
    # -------------------------
    def _insert_attrs(self, cur, node_id, version_id, attrs):

        for attr_id, value in attrs.items():
            dtype = ATTR_TYPES[attr_id]

            if dtype == "num":
                cur.execute("INSERT INTO attr_num VALUES (%s,%s,%s,%s)",
                            (node_id, version_id, attr_id, value))

            elif dtype == "str":
                cur.execute("INSERT INTO attr_str VALUES (%s,%s,%s,%s)",
                            (node_id, version_id, attr_id, value))

            elif dtype == "bool":
                cur.execute("INSERT INTO attr_bool VALUES (%s,%s,%s,%s)",
                            (node_id, version_id, attr_id, value))