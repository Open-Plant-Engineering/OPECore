import time
from opecore.storage.engine import StorageEngine


import os
import time
from opecore.storage.engine import StorageEngine


def test_version_chain(tmp_path):
    db_path = tmp_path / "test.db"
    db = StorageEngine(str(db_path))

    db.append(1, b"Alice")
    t_after_alice = time.time()
    print("t_after_alice =", t_after_alice)

    time.sleep(0.01)
    
    db.append(1, b"Bob")
    t_after_bob = time.time()
    print("t_after_bob =", t_after_bob)

    time.sleep(0.01)
    
    db.append(1, b"Carol")

    print("\n--- READ AS OF ALICE ---")
    result1 = db.read_as_of(1, t_after_alice)
    print("RESULT:", result1)

    print("\n--- READ AS OF BOB ---")
    result2 = db.read_as_of(1, t_after_bob)
    print("RESULT:", result2)

    assert result1 == b"Alice"
    assert result2 == b"Bob"
