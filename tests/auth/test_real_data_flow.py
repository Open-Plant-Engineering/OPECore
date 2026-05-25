import pytest


def test_realistic_claim_flow(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    # ✅ create node (like node_id = 1)
    engine.update_object(1, {
        "name": "Root",
        "type": "Site",
        "owner": None
    }, "system")

    # ✅ create child node
    engine.update_object(2, {
        "name": "Device1",
        "type": "Device",
        "owner": 1
    }, "system")

    # ✅ A claims object 2
    engine.update_object(2, {"claim_by": "A"}, "A")

    # ✅ A modifies
    engine.update_object(2, {"status": "active"}, "A")

    data = engine.read_latest(2)
    assert b"active" in data

    # ❌ B tries modify → should fail
    with pytest.raises(Exception):
        engine.update_object(2, {"status": "inactive"}, "B")

    # ❌ B tries to claim → not allowed
    with pytest.raises(Exception):
        engine.update_object(2, {"claim_by": "B"}, "B")

    # ✅ A releases claim
    engine.update_object(2, {"claim_by": DELETE}, "A")

    data = engine.read_latest(2)
    assert b"claim_by" not in data

    # ✅ Now B can claim
    engine.update_object(2, {"claim_by": "B"}, "B")

    # ✅ B modifies
    engine.update_object(2, {"status": "inactive"}, "B")

    data = engine.read_latest(2)
    assert b"inactive" in data