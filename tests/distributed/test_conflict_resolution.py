def test_cross_node_conflict_resolution(tmp_path):
    from opecore.core.engine import Engine
    import time

    path1 = str(tmp_path / "node1.db")
    path2 = str(tmp_path / "node2.db")

    node1 = Engine(path1)
    node2 = Engine(path2)

    # ✅ same object updated independently
    node1.update_object(1, {"value": 100}, "A")
    time.sleep(0.01)
    node2.update_object(1, {"value": 200}, "A")

    # ✅ sync both ways
    changes1 = node1.get_changes(0)
    changes2 = node2.get_changes(0)

    for c in changes1:
        node2.apply_remote_change(c["object_id"], c["data"])

    for c in changes2:
        node1.apply_remote_change(c["object_id"], c["data"])

    data1 = node1.read_latest(1)
    data2 = node2.read_latest(1)

    # ✅ both nodes must converge
    assert data1 == data2