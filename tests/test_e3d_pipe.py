import tempfile
import os
from opecore.api.db import Database


def test_e3d_pipe_hierarchy():
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "test.db")

        db = Database(path)

        # simulate PIPE node
        pipe = db.insert({
            "Name": b"P-1001",
            "Type": b"PIPE",
            "Zone": b"ZONE-1"
        })

        # update name
        db.update(pipe, {
            "Name": b"P-2001"
        })

        # update zone
        db.update(pipe, {
            "Zone": b"ZONE-2"
        })

        data = db.get(pipe)

        assert data["Name"] == b"P-2001"
        assert data["Type"] == b"PIPE"
        assert data["Zone"] == b"ZONE-2"

        versions = db.get_versions(pipe)

        assert len(versions) == 3

        db.close()
