"""
TEST PURPOSE:
-------------
✅ Partial rollback
✅ Partial rollback preview
✅ Ensure only selected attrs change
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection

DB = "opecore_test_partial"


def test_partial_rollback():

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
        "attrs": {"1": "A", "2": "B", "3": "C"}
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
        "changes": {"2": "X", "4": 100}
    }, headers=headers)

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v2 = cur.fetchone()["current_version"]

    # ----------------------------
    # preview partial rollback
    # ----------------------------
    res = client.post("/node/rollback-preview", json={
        "node_id": node_id,
        "target_version": v1,
        "attr_ids": ["2"]
    })

    changes = res.json()["changes"]

    assert "2" in changes
    assert changes["2"]["type"] == "updated"

    # ----------------------------
    # apply partial rollback
    # ----------------------------
    res = client.post("/node/rollback", json={
        "node_id": node_id,
        "target_version": v1,
        "attr_ids": ["2"]
    }, headers=headers)

    assert res.status_code == 200

    # verify state
    res = client.get(f"/node/{node_id}")
    data = res.json()["data"]

    # ✅ only attr 2 restored
    assert data["2"] == "B"

    # ✅ attr 4 still exists
    assert data["4"] == 100

    # ✅ attr 1 unchanged
    assert data["1"] == "A"