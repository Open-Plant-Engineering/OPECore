import pytest
import threading


def test_claim_force_invalidates_transaction(tmp_path):
    from opecore.core.engine import Engine
    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})

    # admin force removes claim
    engine.update_object(1, {"claim_by": DELETE}, "admin", force=True)

    # ❌ txn must fail now
    with pytest.raises(Exception):
        txn.commit()
    
def test_thread_invalidation(tmp_path):
    from opecore.core.engine import Engine
    import threading
    import pytest

    from opecore.core.constants import DELETE

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})

    def admin():
        engine.update_object(1, {"claim_by": DELETE}, "admin", force=True)

    t = threading.Thread(target=admin)
    t.start()
    t.join()

    with pytest.raises(Exception):
        txn.commit()

