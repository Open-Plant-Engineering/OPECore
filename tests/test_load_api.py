"""
TEST PURPOSE:
-------------
Simulate concurrent API load inside pytest.

IMPORTANT:
-----------
TestClient is NOT a real HTTP server,
so latency numbers are NOT reliable.

We validate:
✅ requests complete successfully
✅ system handles concurrency
✅ reasonable throughput
"""

import time
from concurrent.futures import ThreadPoolExecutor

from tests.db_utils import reset_database
from tests.api_utils import create_test_client
from opecore.db.connection import DBConnection


DB = "opecore_load_test"


def test_load_api():

    # ----------------------------
    # 1. RESET DATABASE
    # ----------------------------
    reset_database(DB)

    direct_dsn = f"postgresql://postgres:postgres@localhost:5432/{DB}"
    DBConnection(direct_dsn).init_db()

    pgbouncer_dsn = f"postgresql://postgres@127.0.0.1:6432/{DB}"
    client = create_test_client(pgbouncer_dsn)

    user = "user1"

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
        },
        "user": user
    })

    assert res.status_code == 200
    node_id = res.json()["node_id"]

    client.post("/node/claim", json={
        "node_id": node_id,
        "user": user
    })

    # ----------------------------
    # 3. WARM-UP
    # ----------------------------
    client.get(f"/node/{node_id}")

    # ----------------------------
    # 4. WORKER
    # ----------------------------
    def worker():
        r = client.get(f"/node/{node_id}")
        assert r.status_code == 200
        return 1

    # ----------------------------
    # 5. LOAD TEST
    # ----------------------------
    num_requests = 200

    start_total = time.time()

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(lambda _: worker(), range(num_requests)))

    total_time = time.time() - start_total

    # ----------------------------
    # 6. RESULTS
    # ----------------------------
    rps = num_requests / total_time

    print("\n===== LOAD TEST RESULTS =====")
    print(f"Total requests: {num_requests}")
    print(f"Total time: {total_time:.4f}s")
    print(f"Requests/sec: {rps:.2f}")

    # ----------------------------
    # 7. ASSERTIONS (REALISTIC)
    # ----------------------------

    # ✅ all requests succeeded
    assert sum(results) == num_requests

    # ✅ system did not degrade completely
    assert rps > 5   # very relaxed (TestClient limitation)