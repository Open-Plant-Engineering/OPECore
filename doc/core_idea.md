***

# 📘 EVA Database — Distributed File-Based Database Design (Phase 1)

***

# 🔥 1. Vision

We are building a:

> ✅ **Distributed, append-only, versioned database engine over shared storage (NAS / file system)**

Inspired by:

* Git (append-only + CAS)
* Datomic (immutability)
* Engineering systems (AVEVA-like hierarchy)

***

# 🧠 2. Core Philosophy

```
✔ Append-only storage
✔ Strong correctness over performance
✔ Distributed via shared filesystem (no network dependency)
✔ Leader-based coordination
✔ Fine-grained hierarchical locking
✔ Simple, extensible architecture
```

***

# 🏗️ 3. Phase 1 Goal (Minimal System)

Build ONLY:

```
✔ Safe storage to shared file
✔ Coordinated multi-user writes
✔ Leader-based serialization
✔ Hierarchical claim system
✔ NAS-safe operations
```

❌ No query engine yet  
❌ No indexing yet  
❌ No typed storage yet

***

# 📁 4. Storage Model

***

## ✅ Structure

```
eva/
│
├── db_1/
│   ├── data.log            # append-only main DB
│   ├── queue/              # user requests
│   ├── claims.json         # active locks
│   ├── precommit/          # optional staging
│   └── leader.info         # leader state
```

***

## ✅ Log Design

```
append-only binary records

[Length][Data][Checksum]
```

***

## ✅ Guarantees

✔ No overwrite  
✔ Crash-safe recovery  
✔ Sequential consistency

***

# 👑 5. Leader-Based Architecture

***

## ✅ Concept

```
Only ONE leader per DB writes to data.log
```

***

## ✅ Responsibilities

Leader handles:

```
✔ claim
✔ unclaim
✔ write (append)
✔ request processing
```

***

## ✅ Clients

Clients:

```
✔ create request in queue
✔ wait for leader
✔ never write to DB directly
```

***

## ✅ Benefit

✔ no file corruption  
✔ no concurrent writes  
✔ simple and safe

***

# 📬 6. Queue System

***

## ✅ Request lifecycle

```
req.txt
→ req.processing
→ req.done / req.failed
```

***

## ✅ Design principles

✔ atomic rename  
✔ retry-safe  
✔ idempotent

***

***

# 🧠 7. Hierarchical Claim System (CORE)

***

# ✅ 7.1 Goal

Manage safe concurrent editing of hierarchical data:

```
/site/zone/pipe1
```

***

# ✅ 7.2 Claim Model

```json
{
  "path": "/site/zone",
  "type": "EXACT | SUBTREE",
  "owner": "session_id"
}
```

***

# ✅ 7.3 Claim Types

***

### 🔷 EXACT

```
Locks only that node
```

Example:

```
/site/zone (EXACT)
```

✔ allows children  
✔ blocks same node

***

***

### 🔷 SUBTREE

```
Locks node + ALL descendants
```

Example:

```
/site/zone (SUBTREE)
/site/zone/*
```

✔ blocks everything below

***

# ⚖️ 7.4 Locking Rules (IMPORTANT)

***

## ✅ Rule 1 — Same node

```
same path → ❌ blocked
```

***

## ✅ Rule 2 — SUBTREE blocks descendants

```
/site/zone SUBTREE
→ blocks /site/zone/pipe1
```

***

## ✅ Rule 3 — EXACT allows children

```
/site/zone EXACT
→ allows /site/zone/pipe1
```

***

## ✅ Rule 4 — Prevent subtree escalation (CRITICAL)

```
If child exists:
/site/zone/pipe1 (claimed)

Then:
/site/zone SUBTREE → ❌ blocked
```

***

## ✅ Rule 5 — Parent EXACT allowed

```
child exists:
/site/zone/pipe1

→ /site/zone EXACT ✅ allowed
```

***

## ✅ Rule 6 — Independent siblings

```
/site/zone/pipe1
→ /site/zone/pipe2 ✅ allowed
```

***

# 🧠 7.5 Core Algorithm

```python
def is_ancestor(parent, child):
    return child.startswith(parent + "/")
```

```python
def can_claim(target, claim_type, claims, user):
    for claim in claims:
        path = claim["path"]
        ctype = claim["type"]
        owner = claim["owner"]

        if owner == user:
            continue

        # same node conflict
        if path == target:
            return False

        # prevent subtree escalation
        if claim_type == "SUBTREE":
            if is_ancestor(target, path):
                return False

        # subtree blocks descendants
        if ctype == "SUBTREE":
            if is_ancestor(path, target):
                return False

    return True
```

***

# 🧠 ✅ Key Insight

> ✅ Small locks are allowed  
> ❗ Large locks cannot override existing small locks

***

# 🛡️ 8. NAS-Safe File Layer

***

## ✅ Principles

```
✔ never trust filesystem
✔ retry all operations
✔ write → temp → rename
✔ idempotent operations
```

***

## ✅ Safe Operations

```
safe_write
safe_append
safe_rename
safe_delete
```

***

# 🔁 9. Recovery Logic

***

## ✅ On startup

```
1. scan data.log → validate checksum
2. truncate invalid tail
3. replay precommit
4. recover stuck queue files
5. clean stale locks
```

***

## ✅ Guarantee

✔ no corruption  
✔ no lost writes

***

# ♻️ 10. Idempotency

***

## ✅ Principle

```
same request executed multiple times → same result
```

***

## ✅ How

```
✔ unique request_id
✔ track processed requests
✔ skip duplicates
```

***

***

# ⚡ 11. Performance Model

***

## ✅ Single leader capacity

```
~50–200 ops/sec (with batching)
```

***

## ✅ Scaling behavior

```
Reads → unlimited ✅
Writes → limited by leader ❗
```

***

## ✅ Real usage

```
1000 users possible if:
✔ reads dominate
✔ writes are infrequent
```

***

***

# 🚀 12. Scaling Strategy

***

## ✅ Horizontal scaling

```
DB_1 → Leader_1
DB_2 → Leader_2
DB_3 → Leader_3
```

***

## ✅ Result

```
N DBs → N× performance ✅
```

***

***

# 🧠 13. Future Evolution (NOT NOW)

```
chunk store (CAS)
versioning
distributed sync between nodes
conflict resolution
indexing
```

***

***

# 🔥 FINAL SUMMARY

***

## ✅ System Characteristics

✔ Append-only DB  
✔ Leader-controlled writes  
✔ NAS-safe operations  
✔ Hierarchical locking  
✔ Idempotent + crash-safe  
✔ Distributed via filesystem

***

## 🎯 Core Insight

> ✅ "Allow fine-grained concurrency"
>
> ❗ "Prevent coarse-grained override of active work"

***

***

> “Let’s start implementing Phase 1 based on this design”
