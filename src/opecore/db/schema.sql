-- =========================
-- NODES
-- =========================
CREATE TABLE IF NOT EXISTS nodes (
    node_id UUID PRIMARY KEY,
    class_id INT,
    current_version BIGINT NOT NULL
);

-- =========================
-- VERSIONS (AUDIT ENABLED)
-- =========================
CREATE TABLE IF NOT EXISTS versions (
    version_id BIGSERIAL PRIMARY KEY,
    node_id UUID NOT NULL,
    parent_version BIGINT,
    created_at TIMESTAMP DEFAULT now(),   -- ✅ added
    created_by TEXT
);

-- =========================
-- ATTRIBUTES (IMPORTANT FIX)
-- attr_id → TEXT ✅ (NOT INT)
-- =========================

CREATE TABLE IF NOT EXISTS attr_num (
    node_id UUID,
    version_id BIGINT,
    attr_id TEXT,   -- ✅ FIXED
    value DOUBLE PRECISION,
    PRIMARY KEY (node_id, version_id, attr_id)
);

CREATE INDEX IF NOT EXISTS idx_attr_num_val ON attr_num(attr_id, value);

CREATE TABLE IF NOT EXISTS attr_str (
    node_id UUID,
    version_id BIGINT,
    attr_id TEXT,   -- ✅ FIXED
    value TEXT,
    PRIMARY KEY (node_id, version_id, attr_id)
);

CREATE TABLE IF NOT EXISTS attr_bool (
    node_id UUID,
    version_id BIGINT,
    attr_id TEXT,   -- ✅ FIXED
    value BOOLEAN,
    PRIMARY KEY (node_id, version_id, attr_id)
);

CREATE TABLE IF NOT EXISTS attr_ref (
    node_id UUID,
    version_id BIGINT,
    attr_id TEXT,   -- ✅ FIXED
    ref_node_id UUID,
    PRIMARY KEY (node_id, version_id, attr_id, ref_node_id)
);

CREATE TABLE IF NOT EXISTS attr_deleted (
    node_id UUID,
    version_id BIGINT,
    attr_id TEXT,   -- ✅ FIXED
    PRIMARY KEY(node_id, version_id, attr_id)
);

-- =========================
-- CLAIMS (LOCKING)
-- =========================
CREATE TABLE IF NOT EXISTS claims (
    node_id UUID PRIMARY KEY,
    claimed_by TEXT,
    claimed_at TIMESTAMP DEFAULT now(),   -- ✅ small improvement
    expires_at TIMESTAMP
);