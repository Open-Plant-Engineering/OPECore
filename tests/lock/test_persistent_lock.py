def test_persistent_lock_basic(tmp_path):
    from opecore.lock.persistent import PersistentLockManager

    lock = PersistentLockManager(str(tmp_path))

    assert lock.acquire(1, "__all__", "A") is True
    assert lock.acquire(1, "__all__", "B") is False
    assert lock.release(1, "__all__", "A") is True
    assert lock.acquire(1, "__all__", "B") is True
