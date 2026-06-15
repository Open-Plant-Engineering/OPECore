/*
=====================================================
ATTRIBUTE SETS (KEY OPTIMIZATION)

Instead of storing attributes again & again,
we store IMMUTABLE SNAPSHOTS.

-----------------------------------------------------
REAL EXAMPLE:

V1 (PIPE-1001):
  key=1 (Diameter) → 100
  key=2 (Material) → "CS"

V2:
  key=1 → 150 (changed)
  key=2 → "CS" (same)

-----------------------------------------------------

Instead of duplicating everything:

We create NEW attribute_set only IF changed

-----------------------------------------------------

DE-DUP EXAMPLE:

If another pipe has:
  Diameter = 150
  Material = CS

→ SAME attribute_set reused ✅

=====================================================
*/

CREATE TABLE IF NOT EXISTS attribute_sets (
    id UUID PRIMARY KEY,
    hash BYTEA UNIQUE NOT NULL   -- hash of full set
);


CREATE TABLE IF NOT EXISTS attribute_set_items (
    set_id UUID NOT NULL,
    key INT NOT NULL,            -- numeric key (from JSON schema)
    value_hash BYTEA NOT NULL,
    value_type SMALLINT NOT NULL,
    PRIMARY KEY (set_id, key),

    FOREIGN KEY (set_id) REFERENCES attribute_sets(id)
);