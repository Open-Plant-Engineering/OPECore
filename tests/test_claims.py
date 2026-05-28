from opecore.claims.claims import ClaimManager


def test_exact_same_node_block(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a", "EXACT") is True
    assert cm.claim("user2", "/a", "EXACT") is False


def test_subtree_blocks_children(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a", "SUBTREE") is True
    assert cm.claim("user2", "/a/b", "EXACT") is False


def test_exact_allows_children(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a", "EXACT") is True
    assert cm.claim("user2", "/a/b", "EXACT") is True


def test_prevent_subtree_escalation(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a/b", "EXACT") is True
    assert cm.claim("user2", "/a", "SUBTREE") is False


def test_parent_exact_allowed(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a/b", "EXACT") is True
    assert cm.claim("user2", "/a", "EXACT") is True


def test_siblings_allowed(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a/b", "EXACT") is True
    assert cm.claim("user2", "/a/c", "EXACT") is True


def test_release(tmp_path):
    cm = ClaimManager(str(tmp_path))

    assert cm.claim("user1", "/a", "EXACT") is True

    cm.release("user1", "/a")

    assert cm.claim("user2", "/a", "EXACT") is True
