import time

def test_session_snapshot(tmp_path):
    from opecore.core.engine import Engine
    from opecore.session.session import Session
    import time

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "A", "A")

    session = Session(engine)

    time.sleep(0.001)
    engine.update_attribute(1, "amount", 100, "A")

    data = session.read(1)
    assert b"100" not in data

    session.refresh()

    data = session.read(1)
    assert b"100" in data
