import os
import json
from opecore.storage.safe import safe_write


def init_storage(config):
    config.ensure_dirs()

    # ✅ initialize DB file
    if not os.path.exists(config.db_file):
        safe_write(config.db_file, b"{}")

    # ✅ initialize claims
    if not os.path.exists(config.claims_file):
        safe_write(config.claims_file, b"[]")

    # ✅ leader file optional (created later)

    print("✅ Storage initialized")