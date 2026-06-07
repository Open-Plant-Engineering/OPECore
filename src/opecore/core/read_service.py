from opecore.core.attr_def import ATTR_TYPES, Attr
from opecore.core import cache


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
    def get_node(self, node_id, snapshot_version=None, use_cache=True):

        if snapshot_version is None:
            snapshot_version = self.get_current_version(node_id)

        cache_key = f"node:{node_id}:{snapshot_version}"

        if use_cache:
            cached = cache.get(cache_key)
            if cached is not None:
                return cached

        result = {}
        deleted_attrs = set()

        # ✅ build version chain
        version_chain = []
        version = snapshot_version
        while version:
            version_chain.append(version)
            version = self._get_parent(version)

        # ✅ replay oldest → newest
        for version in reversed(version_chain):

            # ✅ 1. apply attribute deletions
            for attr_id in self._get_deleted_attrs(node_id, version):
                deleted_attrs.add(attr_id)
                result.pop(attr_id, None)

            # ✅ 2. apply attributes
            attrs = self._get_attrs(node_id, version)

            for attr_id, value in attrs.items():
                attr_id = str(attr_id)  # ✅ normalize

                # ✅ skip deleted attrs
                if attr_id in deleted_attrs:
                    continue

                result[attr_id] = value  # ✅ overwrite latest

        # ✅ 3. handle node delete
        if result.get(Attr.DELETED):
            if use_cache:
                cache.set(cache_key, None)
            return None

        if use_cache:
            cache.set(cache_key, result)

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
                result[str(r["attr_id"])] = r["value"]

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

            return [str(r["attr_id"]) for r in cur.fetchall()]

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

    # -------------------------
    # QUERY EXAMPLE
    # -------------------------
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

    def get_history(self, node_id):

        history = []

        with self.conn.cursor() as cur:

            # get all versions for node
            cur.execute("""
            SELECT version_id, parent_version, created_by
            FROM versions
            WHERE node_id=%s
            ORDER BY version_id ASC
            """, (node_id,))

            versions = cur.fetchall()

        for v in versions:
            version_id = v["version_id"]

            # ✅ get snapshot at that version
            snapshot = self.get_node(node_id, snapshot_version=version_id, use_cache=False)

            history.append({
                "version": version_id,
                "user": v["created_by"],
                "data": snapshot
            })

        return history