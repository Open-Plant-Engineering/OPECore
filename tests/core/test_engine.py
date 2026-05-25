import time

def test_update_flow(tmp_path):
    from opecore.core.engine import Engine
    import time

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "userA", "userA")

    time.sleep(0.001)
    t1 = time.time()

    time.sleep(0.001)
    engine.update_attribute(1, "amount", 100, "userA")

    latest = engine.read_latest(1)
    assert b"100" in latest

    old = engine.read_as_of(1, t1)
    assert b"100" not in old
