import pytest


def test_multi_node_claim_flow(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    # ✅ Create tree structure
    engine.update_object(1, {"name": "Root", "owner": None}, "system")
    engine.update_object(2, {"name": "Child1", "owner": 1}, "system")
    engine.update_object(3, {"name": "Child2", "owner": 1}, "system")

    # ✅ User A claims node 2
    engine.update_object(2, {"claim_by": "A"}, "A")

    # ✅ User B claims node 3
    engine.update_object(3, {"claim_by": "B"}, "B")

    # ✅ A updates node 2
    engine.update_object(2, {"status": "active"}, "A")

    # ✅ B updates node 3
    engine.update_object(3, {"status": "inactive"}, "B")

    # ❌ B cannot update node 2
    with pytest.raises(Exception):
        engine.update_object(2, {"status": "broken"}, "B")

    # ❌ A cannot update node 3
    with pytest.raises(Exception):
        engine.update_object(3, {"status": "broken"}, "A")
    
def test_multi_object_transaction(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    # setup
    engine.update_object(1, {"claim_by": "A"}, "A")
    engine.update_object(2, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")

    txn.update(1, {"value": 100})
    txn.update(2, {"value": 200})

    txn.commit()

    data1 = engine.read_latest(1)
    data2 = engine.read_latest(2)

    assert b"100" in data1
    assert b"200" in data2


import pytest

def test_transaction_unauthorized(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("B")

    txn.update(1, {"value": 999})

    with pytest.raises(Exception):
        txn.commit()

def test_force_override_in_workflow(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    # ❌ B blocked normally
    import pytest
    with pytest.raises(Exception):
        engine.update_object(1, {"value": 1}, "B")

    # ✅ admin force
    engine.update_object(1, {"value": 1}, "admin", force=True)

    data = engine.read_latest(1)
    assert b"1" in data

    # ✅ admin removes claim
    engine.update_object(1, {"claim_by": DELETE}, "admin", force=True)

    data = engine.read_latest(1)
    assert b"claim_by" not in data

def test_mixed_user_timeline(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    # A claims
    engine.update_object(1, {"claim_by": "A"}, "A")

    # A updates
    engine.update_object(1, {"amount": 10}, "A")

    # A releases
    engine.update_object(1, {"claim_by": DELETE}, "A")

    # B claims
    engine.update_object(1, {"claim_by": "B"}, "B")

    # B updates
    engine.update_object(1, {"amount": 20}, "B")

    data = engine.read_latest(1)

    assert b"20" in data

