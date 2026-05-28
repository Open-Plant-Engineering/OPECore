from opecore.recovery.idempotency import IdempotencyStore


def test_idempotency_store(tmp_path):
    store = IdempotencyStore(str(tmp_path))

    rid = "req-1"

    assert store.is_processed(rid) is False

    store.mark_processed(rid)

    assert store.is_processed(rid) is True
