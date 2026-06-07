from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection


DB = "opecore_claim_conflict_test"


def test_api_claim_conflict():

    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client()

    user1 = "user1"
    user2 = "user2"

    headers1 = get_auth_headers(client, user1, project=DB)
    headers2 = get_auth_headers(client, user2, project=DB)

    # CREATE
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

    # USER1 CLAIM
    res = client.post("/node/claim", json={
        "node_id": node_id
    }, headers=headers1)

    assert res.status_code == 200

    # USER2 CLAIM → SHOULD FAIL
    res = client.post("/node/claim", json={
        "node_id": node_id
    }, headers=headers2)

    assert res.status_code == 403
