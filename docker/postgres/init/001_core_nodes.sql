/*
=====================================================
CORE NODE TABLE (E3D ANALOGY)

Think in AVEVA E3D hierarchy:

SITE
 └── ZONE
      └── PIPE
           └── VALVE

Each row in this table represents ONE element.

-----------------------------------------------------
REAL EXAMPLE:

NODE: PIPE-1001
type   = "PIPE"
owner  = "PIPING_TEAM"

NODE: VALVE-2001
type   = "VALVE"
owner  = "PIPING_TEAM"

-----------------------------------------------------

NOTE:
- Only identity is stored here
- ALL attributes (diameter, material, etc.)
  are stored in versioned system

=====================================================
*/

CREATE TABLE IF NOT EXISTS nodes (
    id UUID PRIMARY KEY,
    type TEXT NOT NULL,          -- Example: PIPE, VALVE, EQUIP
    owner TEXT NOT NULL,         -- Example: PIPING, HVAC, STRUCT
    current_version_id UUID
);


/*
=====================================================
TREE RELATIONSHIP

E3D Example:

ZONE-A → PIPE-1001
PIPE-1001 → VALVE-2001

=====================================================
*/

CREATE TABLE IF NOT EXISTS node_relations (
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    PRIMARY KEY (parent_id, child_id)
);