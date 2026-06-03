CREATE TABLE IF NOT EXISTS nodes (
    node_id UUID PRIMARY KEY,
    class_id INT,
    current_version BIGINT NOT NULL
);

CREATE TABLE IF NOT EXISTS versions (
    version_id BIGSERIAL PRIMARY KEY,
    node_id UUID NOT NULL,
    parent_version BIGINT,
    created_at TIMESTAMP DEFAULT now(),
    created_by TEXT
);

CREATE TABLE IF NOT EXISTS attr_num (
    node_id UUID,
    version_id BIGINT,
    attr_id INT,
    value DOUBLE PRECISION,
    PRIMARY KEY (node_id, version_id, attr_id)
);

CREATE INDEX IF NOT EXISTS idx_attr_num_val ON attr_num(attr_id, value);

CREATE TABLE IF NOT EXISTS attr_str (
    node_id UUID,
    version_id BIGINT,
    attr_id INT,
    value TEXT,
    PRIMARY KEY (node_id, version_id, attr_id)
);

CREATE TABLE IF NOT EXISTS attr_bool (
    node_id UUID,
    version_id BIGINT,
    attr_id INT,
    value BOOLEAN,
    PRIMARY KEY (node_id, version_id, attr_id)
);

CREATE TABLE IF NOT EXISTS attr_ref (
    node_id UUID,
    version_id BIGINT,
    attr_id INT,
    ref_node_id UUID,
    PRIMARY KEY (node_id, version_id, attr_id, ref_node_id)
);

CREATE TABLE IF NOT EXISTS attr_deleted (
    node_id UUID,
    version_id BIGINT,
    attr_id INT,
    PRIMARY KEY(node_id, version_id, attr_id)
);

CREATE TABLE IF NOT EXISTS claims (
    node_id UUID PRIMARY KEY,
    claimed_by TEXT,
    claimed_at TIMESTAMP,
    expires_at TIMESTAMP
);