from opecore.lock.persistent import PersistentLockManager


def test_persistent_lock(tmp_path):
    lm = PersistentLockManager(str(tmp_path))

    assert lm.acquire(1, "claim_by", "userA") is True
    assert lm.acquire(1, "claim_by", "userB") is False

    assert lm.release(1, "claim_by", "userB") is False
    assert lm.release(1, "claim_by", "userA") is True

    assert lm.acquire(1, "claim_by", "userB") is True