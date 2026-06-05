"""
TEST PURPOSE:
-------------
Validate claim conflict behavior.

Covers:
--------
1. User1 claims a node
2. User2 tries to claim same node → should fail
3. User2 tries to modify without claim → should fail

This ensures:
✅ claim system enforces exclusivity
✅ concurrent modification is prevented
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection
from opecore.core.node_service import NodeService
from opecore.core.claim_service import ClaimService
from opecore.core.attr_def import Attr
from opecore.models.exceptions import ClaimError


DB = "opecore_claim_conflict_test"


def test_claim_conflict():

    # ----------------------------
    # 1. RESET DATABASE
    # ----------------------------
    reset_database(DB)

    db = DBConnection(f"postgresql://postgres:postgres@localhost:5432/{DB}")
    db.init_db()

    conn = db.get_conn()

    service = NodeService(conn)

    user1 = "user1"
    user2 = "user2"

    # ----------------------------
    # 2. CREATE NODE
    # ----------------------------
    node_id = service.create_node(
        1,
        {
            Attr.NAME: "PumpA",
            Attr.OWNER: "Plant1",
            Attr.TYPE: "Pump"
        },
        user1
    )

    # ----------------------------
    # 3. USER1 CLAIMS NODE
    # ----------------------------
    ClaimService.claim(conn, node_id, user1)

    # ----------------------------
    # 4. USER2 TRIES TO CLAIM (FAIL)
    # ----------------------------
    try:
        ClaimService.claim(conn, node_id, user2)
        assert False, "Expected ClaimError"

    except ClaimError:
        assert True

    # ----------------------------
    # 5. USER2 TRIES TO UPDATE (FAIL)
    # ----------------------------
    cur = conn.cursor()
    cur.execute(
        "SELECT current_version FROM nodes WHERE node_id=%s",
        (node_id,)
    )
    v1 = cur.fetchone()["current_version"]

    try:
        service.update_node(node_id, user2, v1, {
            Attr.PRESSURE: 10.0
        })
        assert False, "Expected ClaimError"

    except ClaimError:
        assert True

    # ----------------------------
    # 6. USER1 UPDATE (SUCCESS)
    # ----------------------------
    new_version = service.update_node(node_id, user1, v1, {
        Attr.PRESSURE: 10.0
    })

    assert new_version is not None


def test_api_claim_conflict():

    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client(dsn)

    user1 = "user1"
    user2 = "user2"

    headers1 = get_auth_headers(client, user1)
    headers2 = get_auth_headers(client, user2)

    # create
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {"1": "PumpA", "2": "Plant1", "3": "Pump"}
    }, headers=headers1 )

    assert res.status_code == 200
    
    node_id = res.json()["node_id"]

    # user1 claims
    client.post("/node/claim", json={
        "node_id": node_id,
    }, headers=headers1)

    # user2 tries to claim
    res = client.post("/node/claim", json={
        "node_id": node_id,
    }, headers=headers2)

    assert res.status_code == 403