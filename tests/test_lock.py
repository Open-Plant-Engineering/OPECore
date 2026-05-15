from opecore.lock.manager import LockManager


def test_lock_basic():
    lm = LockManager()

    # acquire lock
    assert lm.acquire(1, "claim_by", "userA") is True

    # cannot acquire again
    assert lm.acquire(1, "claim_by", "userB") is False

    # release by wrong user fails
    assert lm.release(1, "claim_by", "userB") is False

    # release by owner
    assert lm.release(1, "claim_by", "userA") is True

    # now free again
    assert lm.acquire(1, "claim_by", "userB") is True
