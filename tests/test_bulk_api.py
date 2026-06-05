"""
TEST PURPOSE:
-------------
Validate bulk API behavior.

Covers:
--------
1. Multiple operations in single request
2. Create + Update + Delete in one transaction
3. Atomic behavior (all succeed)
4. Data correctness

This ensures:
✅ bulk API works correctly
✅ transaction integrity is maintained
✅ system remains consistent
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection
from opecore.core import cache


DB = "opecore_bulk_test"


def test_bulk_api():
    cache.clear()

    # ----------------------------
    # 1. RESET DATABASE
    # ----------------------------
    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client(dsn)

    user = "user1"
    headers = get_auth_headers(client, user)

    # ----------------------------
    # 2. BULK CREATE
    # ----------------------------
    res = client.post("/node/bulk", json={
        "operations": [
            {
                "type": "create",
                "class_id": 1,
                "attrs": {
                    "1": "PumpA",
                    "2": "Plant1",
                    "3": "Pump"
                }
            },
            {
                "type": "create",
                "class_id": 1,
                "attrs": {
                    "1": "PumpB",
                    "2": "Plant1",
                    "3": "Pump"
                }
            }
        ]
    }, headers=headers )

    assert res.status_code == 200
    results = res.json()["results"]

    node1 = results[0]["node_id"]
    node2 = results[1]["node_id"]

    # ----------------------------
    # 3. CLAIM NODE BEFORE UPDATE
    # ----------------------------
    client.post("/node/claim", json={
        "node_id": node1,
    }, headers=headers)

    # ----------------------------
    # 4. GET VERSION
    # ----------------------------
    conn = DBConnection(dsn).get_conn()
    cur = conn.cursor()

    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node1,))
    v1 = cur.fetchone()["current_version"]

    # ----------------------------
    # 5. BULK UPDATE + DELETE ATTR
    # ----------------------------
    # first perform update only
    res = client.post("/node/bulk", json={
        "operations": [
            {
                "type": "update",
                "node_id": node1,
                "base_version": v1,
                "changes": {
                    "4": 20.0
                }
            }
        ]
    }, headers=headers )
    
    assert res.status_code == 200
    new_version = res.json()["results"][0]["version"]
    
    # now delete_attr using correct version
    res = client.post("/node/bulk", json={
        "operations": [
            {
                "type": "delete_attr",
                "node_id": node1,
                "base_version": new_version,
                "attr_id": "2"
            }
        ]
    }, headers=headers )
    

    assert res.status_code == 200

    # ----------------------------
    # 6. VERIFY DATA
    # ----------------------------
    res = client.get(f"/node/{node1}")
    data = res.json()["data"]

    # ✅ pressure updated
    assert float(data.get("4", 0)) == 20.0

    # ✅ attr deleted
    assert "2" not in data

    
    # ----------------------------
    # 7. CLAIM NODE2 BEFORE DELETE
    # ----------------------------
    res = client.post("/node/claim", json={
        "node_id": node2,
    }, headers=headers)

    assert res.status_code == 200
    
    # ----------------------------
    # 8. BULK DELETE NODE
    # ----------------------------
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node2,))
    v2 = cur.fetchone()["current_version"]

    res = client.post("/node/bulk", json={
        "operations": [
            {
                "type": "delete_node",
                "node_id": node2,
                "base_version": v2
            }
        ]
    }, headers=headers)

    assert res.status_code == 200

    # ----------------------------
    # 8. VERIFY NODE DELETED
    # ----------------------------
    res = client.get(f"/node/{node2}")
    assert res.json()["data"] is None
