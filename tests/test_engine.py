from opecore.core.engine import Engine
import time


def test_update_flow(tmp_path):
    import time

    engine = Engine(str(tmp_path / "test.db"))

    # first write
    engine.update_attribute(1, "claim_by", "Alice", "userA")

    time.sleep(0.1)   # ✅ ensure separation
    t1 = time.time()

    time.sleep(0.1)
    engine.update_attribute(1, "claim_by", "Bob", "userA")

    data_latest = engine.read_latest(1)
    assert b"Bob" in data_latest

    data_old = engine.read_as_of(1, t1)
    assert b"Alice" in data_old