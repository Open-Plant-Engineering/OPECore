
***

# 📘 EVA Database — Hierarchical Claim System

***

# 🔥 1. Overview

The Claim System is responsible for **managing concurrent edits on hierarchical data** (e.g., `/site/zone/pipe1`) in a distributed environment.

It ensures:

* ✅ Safe multi-user collaboration
* ✅ No conflicting modifications
* ✅ High concurrency for independent nodes
* ✅ Controlled escalation of locks

***

# 🧠 2. Design Philosophy

This system is based on the following principles:

```
✔ Fine-grained access first (EXACT locks)
✔ Controlled coarse-grained control (SUBTREE locks)
✔ No lock escalation over active work
✔ Maximum parallelism without corruption
```

***

# 🧱 3. Data Model

Each claim is represented as:

```json
{
  "path": "/site/zone/pipe1",
  "type": "EXACT | SUBTREE",
  "owner": "session_id",
  "timestamp": 1716890000
}
```

***

# 📌 4. Path Structure

Hierarchy is represented using **path notation**:

```
/site
/site/zone
/site/zone/pipe1
/site/zone/pipe1/valve1
```

***

# 🔑 5. Claim Types

***

## ✅ 5.1 EXACT Lock

```
Locks only the specific node
```

### Example:

```
/site/zone (EXACT)
```

### Behavior:

| Operation                | Result    |
| ------------------------ | --------- |
| Claim `/site/zone` again | ❌ Blocked |
| Claim `/site/zone/pipe1` | ✅ Allowed |
| Claim `/site`            | ✅ Allowed |

***

***

## ✅ 5.2 SUBTREE Lock

```
Locks the node and all its descendants
```

### Equivalent to:

```
/site/zone/*
```

### Example:

```
/site/zone (SUBTREE)
```

### Behavior:

| Operation                       | Result                                       |
| ------------------------------- | -------------------------------------------- |
| Claim `/site/zone/pipe1`        | ❌ Blocked                                    |
| Claim `/site/zone/pipe1/valve1` | ❌ Blocked                                    |
| Claim `/site`                   | ✅ Allowed (unless restricted by child rules) |

***

# ⚖️ 6. Locking Rules (CORE LOGIC)

***

## ✅ Rule 1 — Same Node Conflict

```
If same path already claimed → block
```

***

## ✅ Rule 2 — SUBTREE blocks descendants

```
If:
    existing = /site/zone (SUBTREE)
Then:
    /site/zone/* → ❌ blocked
```

***

## ✅ Rule 3 — EXACT does NOT block descendants

```
If:
    existing = /site/zone (EXACT)
Then:
    /site/zone/pipe1 → ✅ allowed
```

***

## ✅ Rule 4 — Prevent SUBTREE escalation

```
If a child is already claimed:
    → Parent SUBTREE claim is NOT allowed
```

***

### Example:

```
existing: /site/zone/pipe1 (EXACT)

new: /site/zone (SUBTREE)
→ ❌ blocked
```

***

## ✅ Rule 5 — Parent EXACT still allowed

```
existing: /site/zone/pipe1

new: /site/zone (EXACT)
→ ✅ allowed
```

***

## ✅ Rule 6 — Sibling independence

```
existing: /site/zone/pipe1

new: /site/zone/pipe2
→ ✅ allowed
```

***

## ✅ Rule 7 — Same Owner Override

```
If owner is same → allow (optional rule)
```

***

# 🧠 7. Conflict Detection Logic

***

## ✅ Helper Function

```python
def is_ancestor(parent, child):
    return child.startswith(parent + "/")
```

***

## ✅ Main Algorithm

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

        # SUBTREE request must ensure no children exist
        if claim_type == "SUBTREE":
            if is_ancestor(target, path):
                return False

        # existing SUBTREE blocks descendants
        if ctype == "SUBTREE":
            if is_ancestor(path, target):
                return False

    return True
```

***

# 🔄 8. Claim Lifecycle

***

## ✅ Claim

```
Client → request claim
Leader → validate using rules
Leader → persist claim
```

***

## ✅ Unclaim

```
Client → release request
Leader → remove claim entry
```

***

## ✅ Expiration (Optional)

```
if current_time - timestamp > timeout:
    consider stale
    allow reclaim
```

***

# 📦 9. Storage Design

***

## ✅ Central Claim Registry

Stored by leader:

```
claims.json
```

***

### Example

```json
{
  "/site/zone": {
    "type": "EXACT",
    "owner": "session_1"
  },
  "/site/zone/pipe1": {
    "type": "EXACT",
    "owner": "session_2"
  }
}
```

***

# 🚀 10. Performance Characteristics

***

## ✅ Efficient operations

* Ancestor check → O(depth)
* Descendant check → O(n) (can optimize later)

***

## ✅ Scales well because

* fine-grained access allowed
* no unnecessary blocking
* minimal contention

***

# ⚠️ 11. Design Trade-offs

***

## ✅ Advantages

✔ High concurrency  
✔ Simple implementation  
✔ Works well for engineering datasets  
✔ No heavy indexing required

***

## ⚠️ Limitations

* Descendant scan may grow with data size
* Requires leader coordination
* No automatic conflict resolution (must be handled later)

***

# 🔥 12. Key Design Insight

***

> ✅ “Small locks are allowed freely”  
> ❗ “Large locks cannot override existing smaller work”

***

This ensures:

```
✔ maximum collaboration
✔ no destructive overrides
✔ predictable behavior
```

***

# 🎯 13. When to Use

This claim system is ideal for:

* Hierarchical engineering data (AVEVA-like) ✅
* CAD / design systems ✅
* Tree-structured metadata ✅
* Multi-user editing environments ✅

***

# ✅ FINAL SUMMARY

***

## ✅ System Guarantees

✔ No conflicting edits  
✔ Safe subtree protection  
✔ Parallel edits where possible  
✔ Controlled lock escalation

***

## 🔥 Core Rule

> ✅ You can claim smaller parts freely  
> ❗ You cannot claim a larger subtree if any part inside is already claimed

***
