"""
TEST PURPOSE:
-------------
✅ Verify pagination
✅ Verify total count
"""

from tests.db_utils import reset_database
from tests.api_utils import create_test_client, get_auth_headers
from opecore.db.connection import DBConnection

DB = "opecore_test_pagination"


def test_history_pagination():

    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(dsn).init_db()

    client = create_test_client(dsn)

    user = "user1"
    headers = get_auth_headers(client, user)

    # create node
    res = client.post("/node/create", json={
        "class_id": 1,
        "attrs": {"1": "A", "2": "B", "3": "C"}
    }, headers=headers)

    node_id = res.json()["node_id"]

    conn = DBConnection(dsn).get_conn()
    cur = conn.cursor()

    client.post("/node/claim", json={"node_id": node_id}, headers=headers)

    # create many versions
    for i in range(1, 6):
        cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
        v = cur.fetchone()["current_version"]

        client.post("/node/update", json={
            "node_id": node_id,
            "base_version": v,
            "changes": {"4": i}
        }, headers=headers)

    # fetch paginated history
    res = client.get(f"/node/{node_id}/history?page=1&limit=2")

    data = res.json()

    assert "total_versions" in data
    assert data["total_versions"] >= 6  # v1 + 5 updates

    assert len(data["history"]) == 2
