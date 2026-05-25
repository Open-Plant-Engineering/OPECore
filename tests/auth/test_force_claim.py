import pytest


def test_force_remove_claim(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    # ✅ A claims object
    engine.update_object(1, {"claim_by": "A"}, "A")

    # ❌ B cannot remove
    with pytest.raises(Exception):
        engine.update_object(1, {"claim_by": DELETE}, "B")

    # ✅ admin/system forces removal
    engine.update_object(1, {"claim_by": DELETE}, "admin", force=True)

    data = engine.read_latest(1)

    assert b"claim_by" not in data

    # ✅ now B can claim
    engine.update_object(1, {"claim_by": "B"}, "B")

    data = engine.read_latest(1)

    assert b"B" in data

def test_force_override_update(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    # ✅ force update bypasses ownership
    engine.update_object(1, {"amount": 999}, "admin", force=True)

    data = engine.read_latest(1)

    assert b"999" in data