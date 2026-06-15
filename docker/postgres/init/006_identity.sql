/*
=====================================================
USER + SESSION SYSTEM

-----------------------------------------------------
REAL EXAMPLE:

User: "atul"

He logs in → session created:

Session: S1 (UUID)


All actions (edit, claim, commit) → tied to session

=====================================================
*/

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY           -- Example: "atul"
);


CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY,
    user_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id) REFERENCES users(id)
);