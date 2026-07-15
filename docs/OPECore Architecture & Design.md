
Open Plant Engineering Core

Version: 0.1 Draft

1. Vision
What is OPECore

OPECore (Open Plant Engineering Core) is a centralized engineering repository server designed to manage engineering objects, hierarchy, attributes, relationships, sessions, claims, change history and synchronization for large scale engineering projects.

The system is inspired by:

AVEVA DB / Dabacon
PDMS / E3D Database Concepts
Git Version Control
Distributed Synchronization Systems
Modern Event-Sourced Architecture

OPECore is not a CRUD application.

It is an Engineering Repository Engine.

The repository is intended to support:

10,000+ concurrent users
Millions to billions of engineering elements
Complete history tracking
Offline editing
Session management
Claim management
Future branch support
Distributed synchronization
2. Technology Stack
Application Layer
Language     : Elixir
Framework    : OTP
API          : gRPC
Serialization: Protocol Buffers

Data Layer
Database  : PostgreSQL
Pooler    : PgBouncer
ORM       : Ecto

Monitoring
Telemetry
OpenTelemetry
Prometheus
Grafana

3. Core Concepts
Repository

Repository represents a logical engineering database.

Examples:

DESIGN
CATA
PADD
ISOD
CONFIG


Each repository owns:

Elements
Values
Sessions
Claims
Changesets
Hierarchy

Element

Fundamental object stored in repository.

Examples:

Pipe
Equipment
Valve
Nozzle
Structure
Zone
Site


Each element is identified by:

ElementKey

High  Int64
Low   Int64


Equivalent to a 128-bit identifier.

Characteristics:

Globally unique
Never reused
Immutable identity
Element Attributes

Attributes are dynamic.

Defined by Data Model.

Example:

Pipe

NAME
BORE
LENGTH
WEIGHT


Example:

Equipment

NAME
VENDOR
WEIGHT
SERVICE


Attributes are not stored as columns.

Repository uses metadata-driven attributes.

4. Data Model

Initially:

XML Files


will define:

Classes
Attributes
Inheritance
Rules


Future versions will store Data Models inside OPECore itself.

5. Class System

Supports inheritance.

Example

EngineeringItem

   ├── Pipe
   ├── Equipment
   └── Structure


Classes may be changed.

Example:

Pipe
↓
Equipment


When changing classes:

Invalid attributes:

BORE
LENGTH


are automatically removed from active state.

History remains preserved.

6. Hierarchy

Repository stores Parent-Child relationships.

Example:

Plant
 └── Area
      └── Unit
            └── Pipe


Storage model:

Parent
Child


Recursive SQL queries will be used.

Example:

WITH RECURSIVE


No materialized path initially.

7. Supported Data Types

Current implementation:

Boolean
String
Real
Reference
Array


Future:

Integer
Date
DateTime
Decimal
Binary
Vector

8. Reference Data Type

References support cross-repository access.

Structure:

RepositoryId
ElementHigh
ElementLow


Examples:

DESIGN -> CATA
DESIGN -> ISOD


Broken references are allowed.

If target element is deleted:

Reference remains.

9. Array Data Type

Arrays can contain:

Boolean
String
Real
Reference
Array


Nested arrays supported.

Example:

[
 true,
 "PIPE",
 12.5,

 [
   false,
   "VALVE"
 ]
]

10. Session System

Repository is session-based.

No modification allowed without active session.

Workflow:

Create Session

Claim

Modify

Save

Commit

Unclaim

End Session


Rules:

Session Required
Claim Required


before modification.

11. Claim System

Claim ownership prevents parallel modification.

Claim scopes:

Single Element
Multiple Elements
Hierarchy


Examples:

Claim Pipe100


or

Claim Area1


Hierarchy claims lock descendants.

Conflict Rules

Example:

UserA claims Area1

UserB claims Pipe100


Result:

Rejected

12. Version Control

OPECore is version-controlled.

Model inspired by Git.

Concepts:

Repository
Session
Changeset
History

Save Rule
1 Save
=
1 Session
=
1 Changeset


Example:

Modify 5000 elements

Save

Changeset #500


One atomic commit.

13. Sequence Numbers

All repository history uses:

SequenceHigh Int64
SequenceLow Int64


128-bit sequence identifiers.

Used for:

Changesets
Synchronization
History

14. Soft Delete

Elements are never physically deleted.

Example:

DeletedInChangeset


Current state:

Deleted


History remains forever.

15. Name Handling

Names are attributes.

Example:

NAME


Special Rule:

Unique per Repository


Name changes are ordinary attribute changes.

History automatically preserved.

16. Value Deduplication

Identical values stored one time only.

Example:

"NORTH"


appears 10 million times.

Stored:

Once


Referenced by:

ValueId


Benefits:

Reduced size
Reduced history growth
Better cache locality
17. Synchronization

Initial Sync:

Download Repository


Client stores local cache.

Future sync:

GetChangesAfter(
 Sequence
)


Returns:

Created
Modified
Deleted
Moved
Claims


Only deltas.

18. Offline Editing

Supported.

Workflow:

Claim

Sync

Disconnect

Modify

Connect

Save

Commit


Claims remain authoritative on server.

19. Branching

Not implemented initially.

Architecture prepared for:

MAIN

 ├─ DESIGN_A
 ├─ DESIGN_B
 └─ DESIGN_C


All primary tables should be branch-aware from day one.

20. Scalability Goals

Users:

10,000+


Elements:

Millions
to
Billions


Repositories:

Unlimited


History:

Permanent
