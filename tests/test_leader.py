from opecore.leader.leader import Leader


def test_become_leader(tmp_path):
    db = tmp_path

    l1 = Leader(str(db))
    l2 = Leader(str(db))

    assert l1.try_become_leader() is True
    assert l2.try_become_leader() is False


def test_is_leader(tmp_path):
    db = tmp_path

    l1 = Leader(str(db))
    l1.try_become_leader()

    assert l1.is_leader() is True

    l2 = Leader(str(db))
    assert l2.is_leader() is False