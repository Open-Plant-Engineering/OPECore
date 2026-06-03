from opecore.db.connection import DBConnection
from opecore.core.node_service import NodeService
from opecore.core.claim_service import ClaimService
from opecore.core.attr_def import Attr

def test_basic_flow():

    db = DBConnection("postgresql://postgres:postgres@localhost:5432/testdb")
    
    db.init_db()

    conn = db.get_conn()

    service = NodeService(conn)

    user = "test_user"

    # CREATE
    node_id = service.create_node(
        class_id=1,
        attrs={
            Attr.NAME: "PumpA",
            Attr.OWNER: "Plant1",
            Attr.TYPE: "Pump",
            Attr.PRESSURE: 5.0
        },
        user=user
    )

    print("Node created:", node_id)

    # CLAIM
    ClaimService.claim(conn, node_id, user)

    cur = conn.cursor()
    cur.execute("SELECT current_version FROM nodes WHERE node_id=%s", (node_id,))
    version = cur.fetchone()["current_version"]

    # UPDATE
    new_version = service.update_node(
        node_id=node_id,
        user=user,
        base_version=version,
        changes={
            Attr.PRESSURE: 25.0
        }
    )

    print("Updated to version:", new_version)

    # DELETE ATTRIBUTE
    service.delete_attr(node_id, user, new_version, Attr.PRESSURE)

    # RELEASE
    ClaimService.release(conn, node_id, user)

    print("✅ Test completed successfully")

if __name__ == "__main__":
    test_basic_flow()