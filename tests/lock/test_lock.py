def test_lock_basic(tmp_path):
    from opecore.lock.manager import LockManager

    lm = LockManager()

    assert lm.acquire(1, "__all__", "A") is True
    assert lm.acquire(1, "__all__", "B") is False

    assert lm.get_owner(1, "__all__") == "A"

    assert lm.release(1, "__all__", "B") is False
    assert lm.release(1, "__all__", "A") is True


def test_persistent_lock(tmp_path):
    from opecore.lock.persistent import PersistentLockManager

    lm = PersistentLockManager(str(tmp_path))

    assert lm.acquire(1, "__all__", "A") is True
    assert lm.acquire(1, "__all__", "B") is False

    assert lm.get_owner(1, "__all__") == "A"

    assert lm.release(1, "__all__", "B") is False
    assert lm.release(1, "__all__", "A") is True
