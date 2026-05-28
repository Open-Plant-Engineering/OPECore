import os
from opecore.storage.safe import safe_write, safe_rename, safe_delete


def test_safe_write(tmp_path):
    file_path = tmp_path / "file.txt"

    result = safe_write(str(file_path), b"hello")

    assert result is True
    assert file_path.read_bytes() == b"hello"


def test_safe_rename(tmp_path):
    src = tmp_path / "a.txt"
    dst = tmp_path / "b.txt"

    src.write_text("data")

    result = safe_rename(str(src), str(dst))

    assert result is True
    assert not src.exists()
    assert dst.read_text() == "data"


def test_safe_delete(tmp_path):
    file_path = tmp_path / "file.txt"
    file_path.write_text("data")

    result = safe_delete(str(file_path))

    assert result is True
    assert not file_path.exists()
