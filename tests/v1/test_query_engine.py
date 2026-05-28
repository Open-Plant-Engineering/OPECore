import tempfile
import os

from opecore.v1.api.database import Database


# ------------------------
# BASIC (existing)
# ------------------------

def test_match():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"name": b"A"})
        oid2 = db.insert({"name": b"B"})

        res = db.query({
            "name": {"match": b"A"}
        })

        assert oid1 in res
        assert oid2 not in res

        db.close()


def test_inset():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"type": b"A"})
        oid2 = db.insert({"type": b"B"})

        res = db.query({
            "type": {"inset": [b"A", b"B"]}
        })

        assert oid1 in res
        assert oid2 in res

        db.close()


def test_not():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"name": b"A"})
        oid2 = db.insert({"name": b"B"})

        res = db.query({
            "name": {"not": {"match": b"A"}}
        })

        assert oid1 not in res
        assert oid2 in res

        db.close()


def test_matchwild():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"name": b"APPLE"})
        oid2 = db.insert({"name": b"BANANA"})

        res = db.query({
            "name": {"matchwild": b"APP"}
        })

        assert oid1 in res
        assert oid2 not in res

        db.close()


def test_and_combination():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"name": b"A", "type": b"X"})
        oid2 = db.insert({"name": b"A", "type": b"Y"})

        res = db.query({
            "name": {"match": b"A"},
            "type": {"match": b"X"}
        })

        assert oid1 in res
        assert oid2 not in res

        db.close()


# ------------------------
# NEW: OR
# ------------------------

def test_or():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"name": b"A"})
        oid2 = db.insert({"type": b"X"})
        oid3 = db.insert({"name": b"B"})

        res = db.query({
            "or": [
                {"name": {"eq": b"A"}},
                {"type": {"eq": b"X"}}
            ]
        })

        assert oid1 in res
        assert oid2 in res
        assert oid3 not in res

        db.close()


# ------------------------
# NEW: Comparisons
# ------------------------

def test_eq_ne():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"age": b"10"})
        oid2 = db.insert({"age": b"20"})

        res_eq = db.query({"age": {"eq": b"10"}})
        res_ne = db.query({"age": {"ne": b"10"}})

        assert oid1 in res_eq
        assert oid2 not in res_eq

        assert oid2 in res_ne
        assert oid1 not in res_ne

        db.close()


def test_gt_gte_lt_lte():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"age": b"10"})
        oid2 = db.insert({"age": b"20"})
        oid3 = db.insert({"age": b"30"})

        res_gt = db.query({"age": {"gt": b"10"}})
        res_gte = db.query({"age": {"gte": b"20"}})
        res_lt = db.query({"age": {"lt": b"30"}})
        res_lte = db.query({"age": {"lte": b"20"}})

        assert oid2 in res_gt and oid3 in res_gt
        assert oid2 in res_gte and oid3 in res_gte
        assert oid1 in res_lt and oid2 in res_lt
        assert oid1 in res_lte and oid2 in res_lte

        db.close()


# ------------------------
# NEW: Sorting
# ------------------------

def test_sort_asc():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"age": b"20"})
        oid2 = db.insert({"age": b"10"})
        oid3 = db.insert({"age": b"30"})

        res = db.query({
            "age": {"ne": b"0"},
            "sort": ("age", "asc")
        })

        assert res == [oid2, oid1, oid3]

        db.close()


def test_sort_desc():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({"age": b"20"})
        oid2 = db.insert({"age": b"10"})
        oid3 = db.insert({"age": b"30"})

        res = db.query({
            "age": {"ne": b"0"},
            "sort": ("age", "desc")
        })

        assert res == [oid3, oid1, oid2]

        db.close()


# ------------------------
# NEW: Complex Query
# ------------------------

def test_complex_query():
    with tempfile.TemporaryDirectory() as tmp:
        db = Database(os.path.join(tmp, "test.db"))

        oid1 = db.insert({
            "name": b"A",
            "type": b"PIPE",
            "age": b"30"
        })

        oid2 = db.insert({
            "name": b"B",
            "type": b"VALVE",
            "age": b"20"
        })

        oid3 = db.insert({
            "name": b"A",
            "type": b"VALVE",
            "age": b"10"
        })

        res = db.query({
            "or": [
                {"type": {"eq": b"PIPE"}},
                {"name": {"eq": b"A"}}
            ],
            "age": {"gte": b"20"},
            "sort": ("age", "asc")
        })

        assert oid1 in res
        assert oid2 not in res   # filtered out by OR+age
        assert oid3 not in res   # age too small

        assert res == [oid1]

        db.close()