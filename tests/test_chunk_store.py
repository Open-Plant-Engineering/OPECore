from opecore.storage.chunk_store import ChunkStore


def test_put_and_get(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))

    cid = store.put("string", "pipe1")

    result = store.get(cid)

    assert result == ("string", "pipe1")


def test_deduplication(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))

    c1 = store.put("string", "pipe1")
    c2 = store.put("string", "pipe1")

    assert c1 == c2  # ✅ same chunk reused


def test_multiple_types(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))

    c1 = store.put("real", 10.5)
    c2 = store.put("bool", True)

    assert store.get(c1) == ("real", 10.5)
    assert store.get(c2) == ("bool", True)


def test_array(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))

    cid = store.put("array", [1, 2, 3])

    assert store.get(cid)[1] == [1, 2, 3]


def test_exists(tmp_path):
    store = ChunkStore(str(tmp_path / "chunks.json"))

    cid = store.put("string", "test")

    assert store.exists(cid) is True
    assert store.exists("fake") is False
