/*
=====================================================
CLAIM SYSTEM (STRICT LOCKING)

Workflow:

1. Claim node
2. Edit node
3. Commit
4. Release

-----------------------------------------------------
REAL EXAMPLE:

Engineer A claims PIPE-1001
→ Engineer B CANNOT edit

Engineer A finishes
→ releases claim

Engineer B can now claim

-----------------------------------------------------

CRASH CASE:

Engineer crashes → claim remains
Admin runs FORCE_RELEASE ✅

=====================================================
*/

CREATE TABLE IF NOT EXISTS node_claims (
    node_id UUID PRIMARY KEY,
    claimed_by UUID NOT NULL,      -- session_id
    claimed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


/*
=====================================================
CLAIM AUDIT LOG

Tracks ALL operations:

CLAIM
RELEASE
FORCE_RELEASE

-----------------------------------------------------
REAL EXAMPLE:

PIPE-1001:

CLAIM by S1
RELEASE by S1
FORCE_RELEASE by ADMIN

=====================================================
*/

CREATE TABLE IF NOT EXISTS claim_audit_log (
    id UUID PRIMARY KEY,
    node_id UUID NOT NULL,
    action TEXT NOT NULL,
    performed_by UUID NOT NULL,   -- session_id
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reason TEXT
);