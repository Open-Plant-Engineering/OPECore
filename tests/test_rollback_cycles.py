"""
TEST PURPOSE:
-------------
✅ Verify multiple delete/restore cycles
✅ Verify rollback to any version
✅ Validate delete ↔ restore toggling works
"""


from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection

DB = "opecore_test_rollback_cycles"


def test_multiple_rollback_cycles():

    # ----------------------------
    # 1. RESET DB
    # ----------------------------
    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client(dsn)

    user = "user1"
    headers = get_auth_headers(client, user)

    # ----------------------------
    # 2. CREATE NODE (v1)
    # ----------------------------
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {
            "1": "PumpA",
            "2": "Plant1",
            "3": "Pump"
        }
    }, headers=headers)

    assert res.status_code == 200
    node_id = res.json()["node_id"]

    conn = DBConnection(dsn).get_conn()
    cur = conn.cursor()

    # ----------------------------
    # 3. DELETE NODE (v2)
    # ----------------------------
    client.post("/node/claim", json={"node_id": node_id}, headers=headers)

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v1 = cur.fetchone()["current_version"]

    res = client.post("/node/delete", json={
        "node_id": node_id,
        "base_version": v1
    }, headers=headers)

    assert res.status_code == 200

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v2 = cur.fetchone()["current_version"]

    # ----------------------------
    # 4. RESTORE TO V1 (v3)
    # ----------------------------
    res = client.post("/node/rollback", json={
        "node_id": node_id,
        "target_version": v1
    }, headers=headers)

    assert res.status_code == 200

    res = client.get(f"/node/{node_id}")
    data = res.json()["data"]

    # ✅ should be alive again
    assert data is not None
    assert data["1"] == "PumpA"

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v3 = cur.fetchone()["current_version"]

    # ----------------------------
    # 5. RESTORE TO V2 (DELETED STATE) → v4
    # ----------------------------
    res = client.post("/node/rollback", json={
        "node_id": node_id,
        "target_version": v2
    }, headers=headers)

    assert res.status_code == 200

    # ✅ should be deleted again
    res = client.get(f"/node/{node_id}")
    data = res.json()["data"]

    assert data is None

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v4 = cur.fetchone()["current_version"]

    # ----------------------------
    # 6. HISTORY VALIDATION
    # ----------------------------
    res = client.get(f"/node/{node_id}/history")
    history = res.json()["history"]

    # ✅ should have 4+ versions
    assert len(history) >= 4

    # last event should be delete
    last = history[-1]
    assert "_node" in last["changes"]
    assert last["changes"]["_node"]["type"] == "deleted"
