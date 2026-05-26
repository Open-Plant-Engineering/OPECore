def test_basic_replication(tmp_path):
    from opecore.core.engine import Engine
    import time

    path1 = str(tmp_path / "node1.db")
    path2 = str(tmp_path / "node2.db")

    node1 = Engine(path1)
    node2 = Engine(path2)

    # ✅ write in node1
    node1.update_object(1, {"value": 100}, "A")

    time.sleep(0.01)

    # ✅ fetch changes
    changes = node1.get_changes(0)

    # ✅ apply to node2
    for change in changes:
        node2.apply_remote_change(change["object_id"], change["data"])

    data = node2.read_latest(1)

    assert b"100" in data