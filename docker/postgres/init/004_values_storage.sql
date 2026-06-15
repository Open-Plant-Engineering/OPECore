/*
=====================================================
VALUE STORAGE (CAS = CONTENT ADDRESSABLE STORAGE)

Goal:
Store identical values ONLY ONCE.

-----------------------------------------------------
REAL EXAMPLE:

1000 pipes have:
  Material = "CS"

Instead of storing 1000 times:
→ stored ONCE

-----------------------------------------------------

SUPPORTED TYPES:

1 = STRING
2 = NUMBER
3 = BOOLEAN
4 = LIST

=====================================================
*/


-- STRING VALUES
/*
Example:
Material = "CS"
Material = "SS"

Stored ONCE per unique value
*/
CREATE TABLE IF NOT EXISTS string_values (
    hash BYTEA PRIMARY KEY,
    value TEXT NOT NULL
);


-- NUMBER VALUES
/*
Example:
Diameter = 100
Diameter = 150
*/
CREATE TABLE IF NOT EXISTS number_values (
    hash BYTEA PRIMARY KEY,
    value DOUBLE PRECISION NOT NULL
);


-- BOOLEAN VALUES
/*
Example:
IsActive = true
*/
CREATE TABLE IF NOT EXISTS bool_values (
    hash BYTEA PRIMARY KEY,
    value BOOLEAN NOT NULL
);


-- LIST VALUES
/*
Example:
Supports = ["SUP1", "SUP2"]

Stored as compact binary (NOT JSON)
*/
CREATE TABLE IF NOT EXISTS list_values (
    hash BYTEA PRIMARY KEY,
    value BYTEA NOT NULL
);