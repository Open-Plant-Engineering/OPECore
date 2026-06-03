from opecore.db.connection import DBConnection
from opecore.core.node_service import NodeService
from opecore.core.read_service import ReadService
from opecore.core.claim_service import ClaimService
from opecore.core.attr_def import Attr
from .db_utils import reset_database

DB = "opecore_test2"


def test_delete_node():

    reset_database(DB)

    db = DBConnection(f"postgresql://postgres:postgres@localhost:5432/{DB}")
    db.init_db()

    conn = db.get_conn()

    service = NodeService(conn)
    read = ReadService(conn)

    user = "user1"

    node_id = service.create_node(
        1,
        {
            Attr.NAME: "PumpA",
            Attr.OWNER: "Plant1",
            Attr.TYPE: "Pump"
        },
        user
    )

    ClaimService.claim(conn, node_id, user)

    cur = conn.cursor()
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    v1 = cur.fetchone()["current_version"]

    service.delete_node(node_id, user, v1)

    result = read.get_node(node_id)

    assert result is None