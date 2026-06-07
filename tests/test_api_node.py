"""
TEST PURPOSE:
-------------
End-to-end API lifecycle test.

Covers:
--------
✅ create
✅ claim
✅ update
✅ read
✅ delete attribute
✅ delete node
✅ release

Ensures:
✅ system works end-to-end correctly
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers

from opecore.db.connection import DBConnection


DB = "opecore_test_api_full"


def test_full_api_flow():

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
    # 2. CREATE NODE
    # ----------------------------
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {
            "1": "PumpA",
            "2": "Plant1",
            "3": "Pump",
            "4": 5.0
        }
    }, headers=headers)

    assert res.status_code == 200
    node_id = res.json()["node_id"]

    # ----------------------------
    # 3. CLAIM
    # ----------------------------
    res = client.post("/node/claim", json={
        "node_id": node_id,
    }, headers=headers)
    assert res.status_code == 200

    # ----------------------------
    # 4. GET VERSION
    # ----------------------------
    conn = DBConnection(dsn).get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT current_version FROM nodes WHERE node_id=%s",
        (node_id,)
    )
    version = cur.fetchone()["current_version"]

    # ----------------------------
    # 5. UPDATE
    # ----------------------------
    res = client.post("/node/update", json={
        "node_id": node_id,
        "base_version": version,
        "changes": {
            "4": 25.0
        }
    }, headers=headers)

    assert res.status_code == 200

    # ----------------------------
    # 6. GET NODE
    # ----------------------------
    res = client.get(f"/node/{node_id}", headers=headers)
    data = res.json()["data"]

    assert data["4"] == 25.0

    # ----------------------------
    # 7. DELETE ATTRIBUTE
    # ----------------------------
    cur.execute(
        "SELECT current_version FROM nodes WHERE node_id=%s",
        (node_id,)
    )
    version = cur.fetchone()["current_version"]

    res = client.post("/node/delete-attr", json={
        "node_id": node_id,
        "base_version": version,
        "attr_id": "4"
    }, headers=headers)

    assert res.status_code == 200

    # verify removed
    res = client.get(f"/node/{node_id}", headers=headers)
    data = res.json()["data"]

    assert "4" not in data

    # ----------------------------
    # 8. DELETE NODE
    # ----------------------------
    cur.execute(
        "SELECT current_version FROM nodes WHERE node_id=%s",
        (node_id,)
    )
    version = cur.fetchone()["current_version"]

    res = client.post("/node/delete", json={
        "node_id": node_id,
        "base_version": version
    }, headers=headers)

    assert res.status_code == 200

    # ----------------------------
    # 9. VERIFY DELETED
    # ----------------------------
    res = client.get(f"/node/{node_id}", headers=headers)
    assert res.json()["data"] is None

    # ----------------------------
    # 10. RELEASE
    # ----------------------------
    res = client.post("/node/release", json={
        "node_id": node_id,
    }, headers=headers)

    assert res.status_code == 200



def test_full_api_flow1():

    # ----------------------------
    # 1. RESET DATABASE
    # ----------------------------
    reset_database(DB)

    # init schema using direct DB
    direct_dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(direct_dsn).init_db()

    # API uses PgBouncer
    pgbouncer_dsn = f"postgresql://postgres@127.0.0.1:6432/{DB}"

    client = create_test_client(pgbouncer_dsn)

    user = "user1"
    headers = get_auth_headers(client, user)

    # CREATE
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {"1": "PumpA", "2": "Plant1", "3": "Pump", "4": 5.0}
    }, headers=headers)

    assert res.status_code == 200

    node_id = res.json()["node_id"]

    # CLAIM
    res = client.post("/node/claim", json={
        "node_id": node_id,
        }, headers= headers)
    assert res.status_code == 200

    # GET VERSION
    conn = DBConnection(direct_dsn).get_conn()
    cur = conn.cursor()
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v = cur.fetchone()["current_version"]

    # UPDATE
    res = client.post("/node/update", json={
        "node_id": node_id,
        "base_version": v,
        "changes": {"4": 25.0}
    }, headers=headers)
    assert res.status_code == 200
