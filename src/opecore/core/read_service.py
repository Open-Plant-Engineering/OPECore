from opecore.core.attr_def import ATTR_TYPES, Attr

class ReadService:

    def __init__(self, conn):
        self.conn = conn

    # -------------------------
    # GET CURRENT VERSION
    # -------------------------
    def get_current_version(self, node_id):
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT current_version FROM nodes WHERE node_id=%s
            """, (node_id,))
            row = cur.fetchone()
            return row["current_version"] if row else None

    # -------------------------
    # GET NODE (SNAPSHOT)
    # -------------------------
    def get_node(self, node_id, snapshot_version=None):

        if snapshot_version is None:
            snapshot_version = self.get_current_version(node_id)

        result = {}
        deleted_attrs = set()

        version = snapshot_version

        while version:

            # ---------
            # 1. Deleted attributes
            # ---------
            for attr_id in self._get_deleted_attrs(node_id, version):
                deleted_attrs.add(attr_id)

                # remove if already added earlier
                if attr_id in result:
                    result.pop(attr_id)

            # ---------
            # 2. Load attributes
            # ---------
            attrs = self._get_attrs(node_id, version)

            for attr_id, value in attrs.items():
                if attr_id not in result and attr_id not in deleted_attrs:
                    result[attr_id] = value

            # ---------
            # 3. Check node deletion
            # ---------
            if result.get(Attr.DELETED) is True:
                return None

            # ---------
            # 4. Move to parent
            # ---------
            version = self._get_parent(version)

        return result

    # -------------------------
    # LOAD ATTRS BY TYPE
    # -------------------------
    def _get_attrs(self, node_id, version_id):

        result = {}

        with self.conn.cursor() as cur:

            # numbers
            cur.execute("""
            SELECT attr_id, value FROM attr_num
            WHERE node_id=%s AND version_id=%s
            """, (node_id, version_id))
            for r in cur.fetchall():
                result[r["attr_id"]] = r["value"]

            # strings
            cur.execute("""
            SELECT attr_id, value FROM attr_str
            WHERE node_id=%s AND version_id=%s
            """, (node_id, version_id))
            for r in cur.fetchall():
                result[r["attr_id"]] = r["value"]

            # bools
            cur.execute("""
            SELECT attr_id, value FROM attr_bool
            WHERE node_id=%s AND version_id=%s
            """, (node_id, version_id))
            for r in cur.fetchall():
                result[r["attr_id"]] = r["value"]

        return result

    # -------------------------
    # DELETED ATTRIBUTES
    # -------------------------
    def _get_deleted_attrs(self, node_id, version_id):

        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT attr_id FROM attr_deleted
            WHERE node_id=%s AND version_id=%s
            """, (node_id, version_id))

            return [r["attr_id"] for r in cur.fetchall()]

    # -------------------------
    # GET PARENT VERSION
    # -------------------------
    def _get_parent(self, version_id):

        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT parent_version FROM versions
            WHERE version_id=%s
            """, (version_id,))

            row = cur.fetchone()
            return row["parent_version"] if row else None

    def query_pressure_gt(self, value):
    
        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT node_id
            FROM attr_num a
            JOIN nodes n USING(node_id)
            WHERE a.attr_id=%s
            AND a.value > %s
            AND a.version_id = n.current_version
            """, (Attr.PRESSURE, value))
    
            return [r["node_id"] for r in cur.fetchall()]
    