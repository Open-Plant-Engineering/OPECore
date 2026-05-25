def test_valid_parent(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"owner": None}, "A")
    engine.update_object(2, {"owner": 1}, "A")  # ✅ valid


import pytest

def test_parent_must_exist(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    with pytest.raises(Exception):
        engine.update_object(2, {"owner": 99}, "A")

import pytest

def test_self_loop(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"owner": None}, "A")

    with pytest.raises(Exception):
        engine.update_object(1, {"owner": 1}, "A")
    
import pytest

def test_cycle_detection(tmp_path):
    from opecore.core.engine import Engine

    engine = Engine(str(tmp_path / "test.db"))

    engine.update_object(1, {"owner": None}, "A")
    engine.update_object(2, {"owner": 1}, "A")
    engine.update_object(3, {"owner": 2}, "A")

    # ❌ attempt to create cycle: 1 -> 3
    with pytest.raises(Exception):
        engine.update_object(1, {"owner": 3}, "A")
    
