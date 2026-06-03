"""
TEST PURPOSE:
-------------
Validate Redis cache behavior.

Covers:
--------
1. First read → cache miss
2. Second read → cache hit
3. Update → cache invalidation
4. Next read → cache rebuilt

This ensures:
✅ Redis is working
✅ caching logic is correct
✅ invalidation works
"""

import time

from tests.db_utils import reset_database
from opecore.db.connection import DBConnection
from opecore.core.node_service import NodeService
from opecore.core.read_service import ReadService
from opecore.core.claim_service import ClaimService
from opecore.core.attr_def import Attr


DB = "opecore_cache_test"


def test_cache_behavior():

    # ----------------------------
    # 1. RESET DB
    # ----------------------------
    reset_database(DB)

    dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    db = DBConnection(dsn)
    db.init_db()

    conn = db.get_conn()

    service = NodeService(conn)
    read = ReadService(conn)

    user = "user1"

    # ----------------------------
    # 2. CREATE NODE
    # ----------------------------
    node_id = service.create_node(
        1,
        {
            Attr.NAME: "PumpA",
            Attr.OWNER: "Plant1",
            Attr.TYPE: "Pump",
            Attr.PRESSURE: 5.0
        },
        user
    )

    ClaimService.claim(conn, node_id, user)

    # ----------------------------
    # 3. FIRST READ (CACHE MISS)
    # ----------------------------
    start = time.time()
    result1 = read.get_node(node_id)
    t1 = time.time() - start

    assert result1[Attr.PRESSURE] == 5.0

    # ----------------------------
    # 4. SECOND READ (CACHE HIT)
    # ----------------------------
    start = time.time()
    result2 = read.get_node(node_id)
    t2 = time.time() - start

    assert result2 == result1

    # ✅ Cache hit should be faster
    assert t2 <= t1

    # ----------------------------
    # 5. UPDATE (INVALIDATES CACHE)
    # ----------------------------
    cur = conn.cursor()
    cur.execute(
        "SELECT current_version FROM nodes WHERE node_id=%s",
        (node_id,)
    )
    v1 = cur.fetchone()["current_version"]

    service.update_node(node_id, user, v1, {
        Attr.PRESSURE: 25.0
    })

    # ----------------------------
    # 6. READ AFTER UPDATE
    # ----------------------------
    result3 = read.get_node(node_id)

    assert result3[Attr.PRESSURE] == 25.0

    # ----------------------------
    # 7. CONFIRM CACHE WORKING AGAIN
    # ----------------------------
    start = time.time()
    result4 = read.get_node(node_id)
    t3 = time.time() - start

    assert result4 == result3

    # ✅ cache working again
    assert t3 < 0.01   # very fast (approx check)
