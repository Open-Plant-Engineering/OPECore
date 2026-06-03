"""
TEST PURPOSE:
 VERSION CONFLICT behavior.-------------

Scenario:
---------
1. User1 creates and updates node
2. User2 tries to update using OLD (stale) version
3. System must REJECT with 409

This ensures:
✅ strict version control
✅ no accidental overwrite
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client

from opecore.db.connection import DBConnection


DB = "opecore_test_api_conflict"

"""
TEST PURPOSE:
-------------
Verify version conflict behavior via API.

Scenario:
---------
1. User1 creates and updates node → creates new version (v2)
2. User2 tries to update using OLD version (v1)
3. System must reject with HTTP 409

This ensures:
✅ strict version enforcement
✅ no stale updates allowed
"""

def test_api_version_conflict():

    # ----------------------------
    # 1. RESET DB (direct PostgreSQL)
    # ----------------------------
    reset_database(DB)

    # Direct DB connection (for schema + reads)
    direct_dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"

    DBConnection(direct_dsn).init_db()

    # PgBouncer connection (for API)
    pgbouncer_dsn = f"postgresql://postgres@127.0.0.1:6432/{DB}"

    client = create_test_client(pgbouncer_dsn)

    user1 = "user1"
    user2 = "user2"

    # ----------------------------
    # 2. CREATE NODE
    # ----------------------------
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {
            "1": "PumpA",
            "2": "Plant1",
            "3": "Pump"
        },
        "user": user1
    })

    assert res.status_code == 200
    node_id = res.json()["node_id"]

    # ----------------------------
    # 3. USER1 CLAIM
    # ----------------------------
    res = client.post("/node/claim", json={
        "node_id": node_id,
        "user": user1
    })
    assert res.status_code == 200

    # ----------------------------
    # 4. GET VERSION v1 (direct DB)
    # ----------------------------
    conn = DBConnection(direct_dsn).get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT current_version FROM nodes WHERE node_id=%s",
        (node_id,)
    )
    v1 = cur.fetchone()["current_version"]

    # ----------------------------
    # 5. USER1 UPDATE → creates v2
    # ----------------------------
    res = client.post("/node/update", json={
        "node_id": node_id,
        "user": user1,
        "base_version": v1,
        "changes": {"5": True}
    })

    assert res.status_code == 200

    # ----------------------------
    # 6. RELEASE USER1
    # ----------------------------
    res = client.post("/node/release", json={
        "node_id": node_id,
        "user": user1
    })
    assert res.status_code == 200

    # ----------------------------
    # 7. USER2 CLAIM
    # ----------------------------
    res = client.post("/node/claim", json={
        "node_id": node_id,
        "user": user2
    })
    assert res.status_code == 200

    # ----------------------------
    # 8. USER2 UPDATE WITH OLD VERSION (v1)
    # ----------------------------
    res = client.post("/node/update", json={
        "node_id": node_id,
        "user": user2,
        "base_version": v1,   # ❗ stale version
        "changes": {"4": 10}
    })

    # ✅ EXPECT VERSION CONFLICT
    assert res.status_code == 409

