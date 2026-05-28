import time
from opecore.leader.leader import Leader


def test_leader_takeover(tmp_path):
    db = tmp_path

    l1 = Leader(str(db))
    l2 = Leader(str(db))

    # First leader wins
    assert l1.try_become_leader() is True
    assert l2.try_become_leader() is False

    # Wait for timeout
    time.sleep(6)

    # Now second should takeover
    assert l2.try_become_leader() is True
    assert l2.is_leader() is True
    assert l1.is_leader() is False
    assert l1.try_become_leader() is False
