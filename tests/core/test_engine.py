import time


def test_update_flow(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "userA")

    time.sleep(0.001)
    t1 = time.time()

    time.sleep(0.001)
    engine.update_attribute(1, "claim_by", "Bob", "userA")

    latest = engine.read_latest(1)
    assert b"Bob" in latest

    old = engine.read_as_of(1, t1)
    assert b"Alice" in old