import time


def test_session_snapshot(tmp_path):
    from opecore.core.engine import Engine
    from opecore.session.session import Session

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_attribute(1, "claim_by", "Alice", "A")

    session = Session(engine)

    time.sleep(0.001)
    engine.update_attribute(1, "claim_by", "Bob", "B")

    # session still sees old version
    data = session.read(1)
    assert b"Alice" in data

    # refresh → now see new value
    session.refresh()

    data = session.read(1)
    assert b"Bob" in data