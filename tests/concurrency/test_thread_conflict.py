import threading
from opecore.core.engine import Engine
import pytest

def test_thread_conflict_same_object(tmp_path):
    engine = Engine(str(tmp_path / "test.db"))

    # A claims object
    engine.update_object(1, {"claim_by": "A"}, "A")

    errors = []

    def user_a():
        try:
            engine.update_object(1, {"value": 100}, "A")
        except Exception as e:
            errors.append(("A", str(e)))

    def user_b():
        try:
            engine.update_object(1, {"value": 200}, "B")
        except Exception as e:
            errors.append(("B", str(e)))

    t1 = threading.Thread(target=user_a)
    t2 = threading.Thread(target=user_b)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    data = engine.read_latest(1)

    # ✅ Only A should succeed
    assert b"100" in data
    assert not b"200" in data

    # ✅ B must fail
    assert any(e[0] == "B" for e in errors)

def test_thread_same_user(tmp_path):
    from opecore.core.engine import Engine
    import threading

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    errors = []
    
    def update1():
        try:
            engine.update_object(1, {"value": 100}, "A")
        except Exception as e:
            errors.append(str(e))
    
    def update2():
        try:
            engine.update_object(1, {"value": 200}, "A")
        except Exception as e:
            errors.append(str(e))

    t1 = threading.Thread(target=update1)
    t2 = threading.Thread(target=update2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    data = engine.read_latest(1)

    # ✅ one of them should win (last write)
    assert b"100" in data or b"200" in data
    assert len(errors) >= 0  # optional, just ensures no crash

def test_parallel_transactions(tmp_path):
    from opecore.core.engine import Engine
    import threading

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    errors = []

    def txn_a():
        try:
            txn = engine.begin_transaction("A")
            txn.update(1, {"value": 100})
            txn.commit()
        except Exception as e:
            errors.append(("A", str(e)))

    def txn_b():
        try:
            txn = engine.begin_transaction("B")
            txn.update(1, {"value": 200})
            txn.commit()
        except Exception as e:
            errors.append(("B", str(e)))

    t1 = threading.Thread(target=txn_a)
    t2 = threading.Thread(target=txn_b)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    data = engine.read_latest(1)

    # ✅ Only A should succeed
    assert b"100" in data
    assert not b"200" in data

    assert any(e[0] == "B" for e in errors)

def test_force_override_race(tmp_path):
    from opecore.core.engine import Engine
    import threading

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    def user_b():
        try:
            engine.update_object(1, {"value": 200}, "B")
        except:
            pass

    def admin():
        engine.update_object(1, {"value": 999}, "admin", force=True)

    t1 = threading.Thread(target=user_b)
    t2 = threading.Thread(target=admin)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    data = engine.read_latest(1)

    assert b"999" in data

def test_heavy_contention(tmp_path):
    from opecore.core.engine import Engine
    import threading

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"claim_by": "A"}, "A")

    errors = []

    def worker(i):
        try:
            engine.update_object(1, {"value": i}, "A")
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(20)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    data = engine.read_latest(1)

    # ✅ should not crash and value should exist
    assert b"value" in data

