/*
=====================================================
PERFORMANCE INDEXES

Optimized for:
- attribute lookup
- version lookup
- claim tracking

=====================================================
*/

CREATE INDEX IF NOT EXISTS idx_attribute_set_items_set
ON attribute_set_items (set_id);

CREATE INDEX IF NOT EXISTS idx_string_values_hash
ON string_values (hash);

CREATE INDEX IF NOT EXISTS idx_number_values_hash
ON number_values (hash);

CREATE INDEX IF NOT EXISTS idx_versions_created_by
ON versions (created_by);

CREATE INDEX IF NOT EXISTS idx_claims_user
ON node_claims (claimed_by);

CREATE INDEX IF NOT EXISTS idx_sessions_user
ON sessions (user_id);