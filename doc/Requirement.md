Here is your **final, clean, structured Requirement Document** — incorporating everything we discussed, including **versioning, claims, snapshot, querying, and delete handling**.

***

# ✅ ✅ SYSTEM REQUIREMENT DOCUMENT

*(Final Version – Production Ready)*

***

# 1. 🎯 OBJECTIVE

The system shall:

* Store **engineering objects (nodes)** similar to SP3D/AVEVA
* Support **10,000+ users (scalable architecture)**
* Provide **safe concurrent editing**
* Maintain **full version history**
* Support **fast attribute-based queries**
* Ensure **consistent snapshot view per user session**
* Allow **safe deletion of nodes and attributes (versioned)**

***

# 2. 🧱 SYSTEM OVERVIEW

***

## 2.1 Architecture

```
[ Client / UI ]
        ↓
[ API Layer (Python / FastAPI) ]
        ↓
[ PgBouncer ]
        ↓
[ PostgreSQL Database ]
```

***

## 2.2 Layer Responsibilities

### ✅ API Layer

* Enforces business logic
* Handles claims and versioning
* Provides safe access
* Manages snapshot consistency

***

### ✅ PostgreSQL

* Stores all data
* Handles indexing and concurrency
* Maintains versioned records

***

### ✅ Python Schema Layer

* Defines attribute IDs
* Defines object classes
* Abstracts DB complexity

***

# 3. 🧠 DATA MODEL

***

## 3.1 Node (Object)

Each node represents an engineering entity:

* Pump
* Valve
* Equipment

***

### Node structure:

* `node_id` (UUID)
* `class_id` (type)
* `attributes` (key-value pairs)

***

## 3.2 Attributes

Defined centrally in Python:

```python
class Attr:
    NAME = 1
    PRESSURE = 2
    ACTIVE = 3
    DELETED = 999   # system attribute
```

***

## 3.3 Datatypes

| Type      | Storage                |
| --------- | ---------------------- |
| Number    | attr\_num              |
| String    | attr\_str              |
| Boolean   | attr\_bool             |
| Reference | attr\_ref              |
| Array     | attr\_array (optional) |

***

# 4. 🔄 VERSIONING SYSTEM

***

## 4.1 Version Model

* Each modification creates a **new version**
* Versions form a **linear chain**

```
v1 → v2 → v3 → v4
```

***

## 4.2 Rules

* ❌ No updates to existing data
* ✅ Always insert new version
* ✅ Store only changed attributes

***

## 4.3 Conflict Handling

A write is rejected if:

```
current_version ≠ user_base_version
```

***

# 5. 📖 SNAPSHOT MANAGEMENT

***

## 5.1 Requirement

Users must see **stable data during session**

***

## 5.2 Implementation

At session start:

```python
snapshot_version = current_version
```

***

## 5.3 Behavior

* All reads use `snapshot_version`
* No mid-session data changes visible

***

✅ Ensures consistency and predictability

***

# 6. 🔐 CONCURRENCY CONTROL

***

## 6.1 Claim System

Only one user can edit a node.

***

### Table:

```sql
claims(node_id, claimed_by, expires_at)
```

***

## 6.2 Rules

* user must claim before edit
* claim expires automatically
* others cannot modify claimed node

***

# 7. 🔍 QUERY SYSTEM

***

## 7.1 Supported Queries

* `pressure > 10`
* attribute-based filtering
* relationship queries

***

## 7.2 Execution

```sql
SELECT node_id
FROM attr_num
WHERE attr_id = PRESSURE
AND value > 10
```

***

✅ Indexed  
✅ Fast  
✅ Scalable

***

# 8. ❌ DELETE HANDLING (CRITICAL)

***

## 8.1 Guiding Principle

> ❌ NEVER physically delete data  
> ✅ ALWAYS use versioned deletion

***

# 8.2 Node Deletion

***

## Implementation:

Add system attribute:

```python
Attr.DELETED = 999
```

***

## Delete operation:

```python
update_node(node_id, {Attr.DELETED: True})
```

***

## Behavior:

* node remains in DB
* marked as deleted in latest version

***

## Query filtering:

Exclude deleted nodes automatically.

***

## Recovery (undelete):

```python
update_node(node_id, {Attr.DELETED: False})
```

***

✅ Fully reversible

***

# 8.3 Attribute Deletion

***

## Implementation

Create table:

```sql
attr_deleted (
    node_id UUID,
    version_id BIGINT,
    attr_id INT
)
```

***

## Behavior

* Attribute is marked deleted at version
* Not included in future reads

***

## Read Logic Update

* skip attributes present in `attr_deleted`

***

✅ Ensures correct snapshot reconstruction

***

# 9. 🗄️ DATABASE TABLES

***

## 9.1 Core Tables

```sql
nodes
versions
```

***

## 9.2 Attribute Tables

```sql
attr_num
attr_str
attr_bool
attr_ref
attr_array (optional)
attr_deleted
```

***

## 9.3 Concurrency

```sql
claims
```

***

✅ Total: **6–7 tables**

***

# 10. ⚙️ SYSTEM OPERATIONS

***

## 10.1 Create Node

* insert version
* insert attributes
* create node

***

## 10.2 Update Node

* validate claim
* validate version
* insert new version
* insert changed attributes

***

## 10.3 Delete Node

* create new version
* set `DELETED = True`

***

## 10.4 Delete Attribute

* insert into `attr_deleted`

***

## 10.5 Read Node

* use snapshot version
* traverse version chain backward
* merge attributes
* skip deleted attributes

***

# 11. 🐍 PYTHON RESPONSIBILITIES

***

## Must handle:

* version logic
* claim validation
* snapshot handling
* query building
* attribute mapping

***

## Developers use:

```python
Pump.PRESSURE
```

***

# 12. ⚡ PERFORMANCE REQUIREMENTS

***

## Must include:

* PgBouncer (connection pooling)
* Indexed queries
* Short transactions
* Batch inserts

***

## Recommended:

* Redis cache
* Horizontal API scaling
* Table partitioning

***

# 13. 💻 HARDWARE TARGET

***

## Development

```
i5, 16GB RAM → ~300–700 users
```

***

## Production (10k users)

```
DB: 32 cores, 128GB RAM, NVMe
API: 3–6 nodes
Redis + PgBouncer
```

***

# 14. 🔐 SAFETY REQUIREMENTS

***

## MUST:

* enforce API layer (no direct DB access)
* validate claims before writes
* reject version conflicts
* log all operations

***

## MUST NOT:

* update existing records
* physically delete data
* expose DB credentials

***

# ✅ ✅ FINAL SYSTEM DEFINITION

***

> 🔷 A **versioned, claim-based, typed-attribute engineering data platform**  
> 🔷 Supporting **snapshot reads, safe deletes, and high concurrency**

***

# 🔥 FINAL ONE-LINE SUMMARY

> ✅ **“A PostgreSQL-backed, versioned object system with Python-controlled logic, snapshot isolation, safe deletion, and API-enforced concurrency.”**

***

# ✅ READY STATE

You now have:

✅ Complete architecture  
✅ Data model  
✅ Delete-safe design  
✅ Scaling strategy  
✅ Implementation roadmap

***

If you want next, I can convert this into:

* 📄 formal PDF spec
* 🧱 system design diagrams
* 🧪 test plan
* 🚀 deployment blueprint

***
