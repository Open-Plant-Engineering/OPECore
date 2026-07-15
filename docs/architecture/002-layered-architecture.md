
# Layered Architecture

## Layer 1

Core Domain

Contains:

- IDs
- Elements
- Values
- Hierarchy
- Changesets

Dependencies:

None

---

## Layer 2

Persistence

Contains:

- Ecto
- PostgreSQL
- Storage

Dependencies:

Domain

---

## Layer 3

Services

Contains:

- Session Service
- Claim Service
- Save Service
- Sync Service

Dependencies:

Domain
Persistence

---

## Layer 4

gRPC

Contains:

- Protobuf
- gRPC Services
- Streaming APIs

Dependencies:

Services
