import pytest

from opecore.db.connection import DBConnection
from opecore.core.node_service import NodeService
from opecore.core.read_service import ReadService
from opecore.core.claim_service import ClaimService
from opecore.core.attr_def import Attr
from opecore.models.exceptions import NodeDeletedError
from .db_utils import reset_database


DB = "opecore_test_delete_conflict"


def test_node_delete_conflict():

    reset_database(DB)

    db = DBConnection(f"postgresql://postgres:postgres@localhost:5432/{DB}")
    db.init_db()

    conn = db.get_conn()

    service = NodeService(conn)
    read = ReadService(conn)

    user1 = "user1"
    user2 = "user2"

    # ----------------------------
    # 1. CREATE NODE
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
    # 2. USER1 CLAIM + DELETE
    # ----------------------------
    ClaimService.claim(conn, node_id, user1)

    cur = conn.cursor()
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v1 = cur.fetchone()["current_version"]

    service.delete_node(node_id, user1, v1)

    ClaimService.release(conn, node_id, user1)

    # ----------------------------
    # 3. USER2 CLAIMS AFTER DELETE
    # ----------------------------
    ClaimService.claim(conn, node_id, user2)

    # user2 tries stale delete/update
    with pytest.raises(NodeDeletedError):
        service.update_node(node_id, user2, v1, {
            Attr.PRESSURE: 10.0
        })

    with pytest.raises(NodeDeletedError):
        service.delete_node(node_id, user2, v1)

    # ----------------------------
    # 4. VERIFY READ RETURNS NONE
    # ----------------------------
    result = read.get_node(node_id)

    assert result is None
