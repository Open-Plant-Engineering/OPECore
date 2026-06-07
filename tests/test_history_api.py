"""
TEST PURPOSE:
-------------
Verify history tracking:
✅ who changed what
✅ version ordering
✅ snapshot correctness
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers

from opecore.db.connection import DBConnection

DB = "opecore_test_history"


def test_history_api():

    # ----------------------------
    # 1. RESET DB
    # ----------------------------
    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client(dsn)

    user1 = "user1"
    user2 = "user2"

    headers1 = get_auth_headers(client, user1)
    headers2 = get_auth_headers(client, user2)

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
    }, headers=headers1)

    assert res.status_code == 200
    node_id = res.json()["node_id"]

    # ----------------------------
    # 3. CLAIM + UPDATE (v2)
    # ----------------------------
    client.post("/node/claim", json={"node_id": node_id}, headers=headers1)

    # get version
    conn = DBConnection(dsn).get_conn()
    cur = conn.cursor()
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v1 = cur.fetchone()["current_version"]

    res = client.post("/node/update", json={
        "node_id": node_id,
        "base_version": v1,
        "changes": {
            "4": 25.0
        }
    }, headers=headers1)

    assert res.status_code == 200

    client.post("/node/release", json={"node_id": node_id}, headers=headers1)

    # ----------------------------
    # 4. USER2 CLAIM + DELETE ATTR (v3)
    # ----------------------------
    client.post("/node/claim", json={"node_id": node_id}, headers=headers2)

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v2 = cur.fetchone()["current_version"]

    res = client.post("/node/delete-attr", json={
        "node_id": node_id,
        "base_version": v2,
        "attr_id": "4"
    }, headers=headers2)

    assert res.status_code == 200

    # ----------------------------
    # 5. FETCH HISTORY
    # ----------------------------
    res = client.get(f"/node/{node_id}/history")

    assert res.status_code == 200

    history = res.json()["history"]

    # ----------------------------
    # 6. VALIDATIONS
    # ----------------------------

    # ✅ we expect 3 versions
    assert len(history) == 3

    # ✅ version 1 (create)
    v1_data = history[0]
    assert v1_data["user"] == user1
    assert v1_data["data"]["1"] == "PumpA"
    assert "4" not in v1_data["data"]

    # ✅ version 2 (update)
    v2_data = history[1]
    assert v2_data["user"] == user1
    assert v2_data["data"]["4"] == 25.0   # added pressure

    # ✅ version 3 (delete attr)
    v3_data = history[2]
    assert v3_data["user"] == user2
    assert "4" not in v3_data["data"]     # removed

    # ----------------------------
    # 7. DELETE NODE (v4)
    # ----------------------------
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v3 = cur.fetchone()["current_version"]

    res = client.post("/node/delete", json={
        "node_id": node_id,
        "base_version": v3
    }, headers=headers2)

    assert res.status_code == 200

    # ----------------------------
    # 8. HISTORY AFTER DELETE
    # ----------------------------
    res = client.get(f"/node/{node_id}/history")

    history = res.json()["history"]

    assert len(history) == 4

    # last version should be deleted
    assert history[-1]["data"] is None
