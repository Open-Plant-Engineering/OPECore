from opecore.core.attr_def import ATTR_TYPES, Attr
from opecore.core import cache
from opecore.core.claim_service import ClaimService

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
                attr_id = str(attr_id)  # ✅ keep consistent (safe)

                if attr_id in deleted_attrs:
                    continue

                result[attr_id] = value

        if Attr.DELETED in result:
            if result[Attr.DELETED] is True:
                return None
        
            if result[Attr.DELETED] is False:
                result.pop(Attr.DELETED)

        # ✅ cache final state
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

    def get_history(self, node_id, user=None, attr_id=None):

        history = []

        with self.conn.cursor() as cur:
            cur.execute("""
            SELECT version_id, parent_version, created_by, created_at
            FROM versions
            WHERE node_id=%s
            ORDER BY version_id ASC
            """, (node_id,))

            versions = cur.fetchall()

        prev_snapshot = None

        for v in versions:
            version_id = v["version_id"]

            current_snapshot = self.get_node(
                node_id,
                snapshot_version=version_id,
                use_cache=False
            )

            # ✅ IMPORTANT FIX: ensure None stays None (not converted to {})
            if current_snapshot is None:
                current_snapshot = None

            # ✅ compute diff vs previous version
            changes = self._compute_diff(prev_snapshot, current_snapshot)

            entry = {
                "version": version_id,
                "user": v["created_by"],
                "timestamp": str(v["created_at"]),
                "changes": changes
            }

            # ✅ FILTER BY USER
            if user and entry["user"] != user:
                continue
            
            # ✅ FILTER BY ATTR
            if attr_id:
                if attr_id not in entry["changes"]:
                    continue
                
            history.append(entry)

            prev_snapshot = current_snapshot

        return history

    def _compute_diff(self, old_data, new_data):

        diff = {}

        old_data = old_data or {}
        new_data = new_data or {}

        # ✅ NODE-LEVEL DELETE DETECTION
        if old_data and not new_data:
            return {
                "_node": {
                    "type": "deleted"
                }
            }

        all_keys = set(old_data.keys()).union(new_data.keys())

        for key in all_keys:

            old_val = old_data.get(key)
            new_val = new_data.get(key)

            if key not in old_data:
                diff[key] = {
                    "type": "added",
                    "value": new_val
                }

            elif key not in new_data:
                diff[key] = {
                    "type": "removed",
                    "old_value": old_val
                }

            elif old_val != new_val:
                diff[key] = {
                    "type": "updated",
                    "old_value": old_val,
                    "new_value": new_val
                }

        return diff

    def preview_rollback(self, node_id, target_version, attr_ids=None):

        current_state = self.get_node(node_id, use_cache=False)
        target_state = self.get_node(
            node_id,
            snapshot_version=target_version,
            use_cache=False
        )

        if current_state is None:
            current_state = {}

        if target_state is None:
            target_state = {}

        # ✅ partial logic
        if attr_ids:
            simulated = dict(current_state)

            for attr in attr_ids:
                if attr in target_state:
                    simulated[attr] = target_state[attr]
                else:
                    simulated.pop(attr, None)
        else:
            simulated = dict(target_state)

        # ✅ compute diff
        diff = self._compute_diff(current_state, simulated)

        return diff