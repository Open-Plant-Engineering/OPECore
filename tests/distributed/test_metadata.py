import os
import uuid


def test_node_id_created_and_persisted(tmp_path):
    from opecore.core.engine import Engine

    db_path = str(tmp_path / "test.db")

    engine1 = Engine(db_path)
    node_id_1 = engine1.node_id

    # ✅ must exist
    assert node_id_1 is not None
    assert isinstance(uuid.UUID(node_id_1), uuid.UUID)

    # ✅ new engine should reuse same node_id
    engine2 = Engine(db_path)
    node_id_2 = engine2.node_id

    assert node_id_1 == node_id_2


def test_metadata_present_on_update_object(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"value": 100}, "A")

    data = engine.read_latest(1)
    assert data is not None

    obj = engine._deserialize(data)

    # ✅ metadata fields must exist
    assert "__version" in obj
    assert "__node_id" in obj
    assert "__ts" in obj

    # ✅ non-transaction → txn_id should be None
    assert "__txn_id" in obj
    assert obj["__txn_id"] is None


def test_metadata_present_on_transaction_commit(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    txn = engine.begin_transaction("A")
    txn.update(1, {"value": 100})
    txn.commit()

    data = engine.read_latest(1)
    obj = engine._deserialize(data)

    # ✅ transaction metadata
    assert "__txn_id" in obj
    assert obj["__txn_id"] is not None

    assert "__node_id" in obj
    assert obj["__node_id"] == engine.node_id

    assert "__ts" in obj


def test_multiple_updates_increment_version_and_metadata(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"value": 10}, "A")
    data1 = engine._deserialize(engine.read_latest(1))

    engine.update_object(1, {"value": 20}, "A")
    data2 = engine._deserialize(engine.read_latest(1))

    # ✅ version increments
    assert data2["__version"] == data1["__version"] + 1

    # ✅ metadata preserved
    assert "__node_id" in data2
    assert "__ts" in data2


def test_metadata_survives_restart(tmp_path):
    from opecore.core.engine import Engine

    db_path = str(tmp_path / "test.db")

    engine = Engine(db_path)
    engine.update_object(1, {"value": 42}, "A")

    # restart engine
    engine = Engine(db_path)

    data = engine.read_latest(1)
    obj = engine._deserialize(data)

    # ✅ metadata still present
    assert "__node_id" in obj
    assert "__version" in obj
    assert "__ts" in obj