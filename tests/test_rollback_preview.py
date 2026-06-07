"""
TEST PURPOSE:
-------------
✅ Verify rollback preview (dry-run)
✅ Ensure no DB change happens
✅ Validate diff correctness
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection

DB = "opecore_test_preview"


def test_rollback_preview():

    # ----------------------------
    # setup
    # ----------------------------
    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client(dsn)

    user = "user1"
    headers = get_auth_headers(client, user)

    # ----------------------------
    # create node (v1)
    # ----------------------------
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {"1": "PumpA", "2": "Plant1", "3": "Pump"}
    }, headers=headers)

    node_id = res.json()["node_id"]

    conn = DBConnection(dsn).get_conn()
    cur = conn.cursor()

    # ----------------------------
    # update (v2)
    # ----------------------------
    client.post("/node/claim", json={"node_id": node_id}, headers=headers)

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v1 = cur.fetchone()["current_version"]

    client.post("/node/update", json={
        "node_id": node_id,
        "base_version": v1,
        "changes": {"4": 25.0}
    }, headers=headers)

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v2 = cur.fetchone()["current_version"]

    # ----------------------------
    # preview rollback to v1
    # ----------------------------
    res = client.post("/node/rollback-preview", json={
        "node_id": node_id,
        "target_version": v1
    }, headers=headers)

    assert res.status_code == 200

    changes = res.json()["changes"]

    # ✅ attr 4 should be removed
    assert "4" in changes
    assert changes["4"]["type"] == "removed"

    # ----------------------------
    # ensure NO actual rollback happened
    # ----------------------------
    res = client.get(f"/node/{node_id}", headers=headers)
    data = res.json()["data"]

    assert "4" in data  # still exists!

    # ----------------------------
    # preview rollback to v2 (no changes expected)
    # ----------------------------
    res = client.post("/node/rollback-preview", json={
        "node_id": node_id,
        "target_version": v2
    }, headers=headers)

    changes = res.json()["changes"]

    # ✅ no changes (same state)
    assert changes == {}
