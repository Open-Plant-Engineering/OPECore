import pytest
import threading
import time


def test_transaction_invalidated_on_external_update(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    # ✅ initial state
    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})

    # ✅ external update (simulate another actor)
    engine.update_object(1, {"value": 200}, "B", force=True)

    # ✅ txn must now be invalidated
    with pytest.raises(Exception):
        txn.commit()


def test_transaction_invalidated_by_force_update(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})

    # ✅ admin force change
    engine.update_object(1, {"claim_by": DELETE}, "admin", force=True)

    with pytest.raises(Exception):
        txn.commit()


def test_transaction_not_invalidated_by_own_changes(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})

    # ✅ same actor update through txn
    txn.commit()

    # ✅ no failure expected
    data = engine.read_latest(1)
    assert b"100" in data


def test_transaction_invalidated_in_thread(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})

    def updater():
        time.sleep(0.01)
        engine.update_object(1, {"value": 999}, "B", force=True)

    t = threading.Thread(target=updater)
    t.start()
    t.join()

    # ✅ txn should fail due to invalidation
    with pytest.raises(Exception):
        txn.commit()