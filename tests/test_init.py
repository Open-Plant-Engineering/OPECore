from opecore.config import Config
from opecore.setup.init import init_storage
import os


def test_init_storage(tmp_path):
    cfg = Config(str(tmp_path))

    init_storage(cfg)

    assert os.path.exists(cfg.db_file)
    assert os.path.exists(cfg.claims_file)
    assert os.path.exists(cfg.wal_dir)