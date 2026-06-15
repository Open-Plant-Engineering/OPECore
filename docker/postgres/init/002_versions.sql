/*
=====================================================
VERSIONS (LIKE GIT COMMITS / E3D REVISIONS)

Every change creates a new version.

-----------------------------------------------------
REAL EXAMPLE:

PIPE-1001 Version History:

V1:
  Diameter = 100
  Material = CS

V2:
  Diameter = 150  (changed)
  Material = CS

-----------------------------------------------------

VERSION CHAIN:

V1 → V2 → V3

-----------------------------------------------------

SESSION EXAMPLE:

Engineer Atul logs in → Session S1
Engineer modifies PIPE → Version created by S1

=====================================================
*/

CREATE TABLE IF NOT EXISTS versions (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL,
    parent_version_id UUID,          -- Previous version
    attribute_set_id UUID NOT NULL,  -- Snapshot of all attributes
    created_by UUID NOT NULL,        -- session_id
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS idx_versions_node
ON versions (node_id);
