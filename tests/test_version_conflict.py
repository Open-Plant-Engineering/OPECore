import pytest

from opecore.db.connection import DBConnection
from opecore.core.node_service import NodeService
from opecore.core.read_service import ReadService
from opecore.core.claim_service import ClaimService
from opecore.core.attr_def import Attr
from opecore.models.exceptions import VersionConflictError
from .db_utils import reset_database

DB = "opecore_test3"


def test_version_conflict():

    reset_database(DB)

    db = DBConnection(f"postgresql://postgres:postgres@localhost:5432/{DB}")
    db.init_db()

    conn = db.get_conn()

    service = NodeService(conn)
    read = ReadService(conn)

    user1 = "user1"
    user2 = "user2"

    node_id = service.create_node(
        1,
        {
            Attr.NAME: "PumpA",
            Attr.OWNER: "Plant1",
            Attr.TYPE: "Pump"
        },
        user1
    )

    ClaimService.claim(conn, node_id, user1)

    cur = conn.cursor()
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v1 = cur.fetchone()["current_version"]

    service.update_node(node_id, user1, v1, {Attr.ACTIVE: True})

    ClaimService.release(conn, node_id, user1)

    # user2 stale update
    ClaimService.claim(conn, node_id, user2)

    with pytest.raises(VersionConflictError):
        service.update_node(node_id, user2, v1, {Attr.PRESSURE: 10})

    latest = read.get_node(node_id)

    assert latest[Attr.ACTIVE] is True
