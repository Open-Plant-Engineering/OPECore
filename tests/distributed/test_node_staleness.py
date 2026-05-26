import pytest
import time


def test_stale_node_blocks_update(tmp_path):
    from opecore.core.engine import Engine

    path1 = str(tmp_path / "node1.db")
    path2 = str(tmp_path / "node2.db")

    node1 = Engine(path1)
    node2 = Engine(path2)

    # ✅ initial sync
    node1.update_object(1, {"value": 100}, "A")

    changes = node1.get_changes(0)
    for c in changes:
        node2.apply_remote_change(c["object_id"], c["data"])

    # ✅ node1 updates again
    time.sleep(0.01)
    node1.update_object(1, {"value": 200}, "A")

    # ✅ node2 KNOWS about new version but does NOT apply it
    latest_changes = node1.get_changes(0)
    for c in latest_changes:
        obj = c["data"]
        node2.latest_seen_version[c["object_id"]] = obj.get("__version", 0)

    # ❌ should block update
    with pytest.raises(Exception):
        node2.update_object(1, {"value": 300}, "B")


def test_stale_transaction_blocked(tmp_path):
    from opecore.core.engine import Engine

    path1 = str(tmp_path / "node1.db")
    path2 = str(tmp_path / "node2.db")

    node1 = Engine(path1)
    node2 = Engine(path2)

    # ✅ initial sync
    node1.update_object(1, {"value": 100}, "A")

    changes = node1.get_changes(0)
    for c in changes:
        node2.apply_remote_change(c["object_id"], c["data"])

    # ✅ node1 updates again
    time.sleep(0.01)
    node1.update_object(1, {"value": 200}, "A")

    # ✅ simulate stale knowledge (without applying)
    latest_changes = node1.get_changes(0)
    for c in latest_changes:
        obj = c["data"]
        node2.latest_seen_version[c["object_id"]] = obj.get("__version", 0)

    txn = node2.begin_transaction("B")

    # ❌ txn must fail
    with pytest.raises(Exception):
        txn.update(1, {"value": 999})


def test_update_allowed_after_sync(tmp_path):
    from opecore.core.engine import Engine

    path1 = str(tmp_path / "node1.db")
    path2 = str(tmp_path / "node2.db")

    node1 = Engine(path1)
    node2 = Engine(path2)

    # ✅ initial write + sync
    node1.update_object(1, {"value": 100}, "A")
    changes = node1.get_changes(0)
    for c in changes:
        node2.apply_remote_change(c["object_id"], c["data"])

    # ✅ node1 updates again
    node1.update_object(1, {"value": 200}, "A")

    # ✅ node2 knows newer version
    latest_changes = node1.get_changes(0)
    for c in latest_changes:
        obj = c["data"]
        node2.latest_seen_version[c["object_id"]] = obj.get("__version", 0)

    # ✅ now APPLY changes → becomes fresh
    for c in latest_changes:
        node2.apply_remote_change(c["object_id"], c["data"])

    # ✅ now update should work
    node2.update_object(1, {"value": 300}, "B", force=True)

    data = node2.read_latest(1)
    assert b"300" in data


def test_is_stale_flag(tmp_path):
    from opecore.core.engine import Engine

    path1 = str(tmp_path / "node1.db")
    path2 = str(tmp_path / "node2.db")

    node1 = Engine(path1)
    node2 = Engine(path2)

    # ✅ initial sync
    node1.update_object(1, {"value": 100}, "A")

    changes = node1.get_changes(0)
    for c in changes:
        node2.apply_remote_change(c["object_id"], c["data"])

    assert not node2.is_stale(1)

    # ✅ node1 updates
    node1.update_object(1, {"value": 200}, "A")

    # ✅ node2 learns about new version but does not apply
    latest_changes = node1.get_changes(0)
    for c in latest_changes:
        obj = c["data"]
        node2.latest_seen_version[c["object_id"]] = obj.get("__version", 0)

    # ✅ now must be stale
    assert node2.is_stale(1)