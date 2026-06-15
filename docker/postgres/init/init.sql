-- =========================
-- SCHEMA
-- =========================
CREATE SCHEMA IF NOT EXISTS public;

-- =========================
-- TABLE: USERS
-- =========================
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- INDEXES
-- =========================
CREATE INDEX IF NOT EXISTS idx_users_email
ON users (email);

-- =========================
-- SEED DATA
-- =========================
INSERT INTO users (id, name, email)
VALUES 
('11111111-1111-1111-1111-111111111111', 'Atul', 'atul@test.com')
ON CONFLICT (id) DO NOTHING;

-- =========================
-- FUTURE: EXTENSIONS
-- =========================
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";