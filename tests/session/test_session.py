import time

def test_session_snapshot(tmp_path):
    from opecore.core.engine import Engine
    from opecore.session.session import Session
    import time

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "A", "A")

    session = Session(engine)

    time.sleep(0.01)
    engine.update_attribute(1, "amount", 100, "A")
    time.sleep(0.01)
    data = session.read(1)
    assert b"100" not in data
    time.sleep(0.01)
    session.refresh()
    time.sleep(0.01)
    data = session.read(1)
    assert b"100" in data
