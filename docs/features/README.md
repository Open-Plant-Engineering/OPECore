
# Feature Documentation Standard

Every feature must have a corresponding feature document.

Example:

001-element-id.md
002-sequence-id.md
003-value.md

Every feature document must contain:

- Purpose
- Dependencies
- Files To Create
- Files To Modify
- Public Interfaces
- Tests
- Future Extensions
- Do Not Modify
- AI Prompt

No feature should be implemented without a feature document.

# OPECore Development Execution Roadmap

Version: 1.0

Author: Atul K

Project: Open Plant Engineering Core (OPECore)

---

# Purpose

This roadmap defines the exact execution order for building OPECore as a solo developer using AI assistance.

The objective is to:

- Build stable foundations first
- Avoid future rewrites
- Keep every feature independently testable
- Allow AI to work feature-by-feature
- Minimize architectural mistakes
- Support future growth to billions of elements and 10K+ users

---

# Development Rules

## Rule 1

Build from the center outward.

Never start with:

- gRPC
- Claims
- Sessions
- Sync

Start with:

- Domain
- Storage
- Versioning

---

## Rule 2

Every feature must have:

- Feature Document
- Boundaries
- Tests
- Acceptance Criteria
- AI Prompt

before implementation starts.

---

## Rule 3

Every feature must be independently testable.

---

## Rule 4

Every feature should be implementable in a single AI conversation.

---

## Rule 5

No future rewrites.

Build the correct architecture from the beginning.

---

# Phase 0
# Project Bootstrap

Goal:

Create project structure and documentation foundation.

Duration:

2-3 Days

---

## F-0001 Create Umbrella Project

Tasks:

- Create Umbrella Project
- Configure Mix
- Configure Applications

Deliverables:

- Project Builds
- Project Tests Run

---

## F-0002 Configure Development Tools

Tasks:

- Formatter
- Credo
- Dialyzer
- ExUnit

Deliverables:

- Static Analysis Ready

---

## F-0003 Configure Git

Tasks:

- Git Repository
- GitHub Repository
- Branching Strategy

Deliverables:

- Source Control Ready

---

## F-0004 Documentation Structure

Create:

docs/

docs/architecture/

docs/features/

docs/adr/

docs/prompts/

docs/milestones/

Deliverables:

- Documentation Ready

---

# Phase 1
# Identity Foundation

Goal:

Create repository identity system.

Everything depends on these IDs.

Duration:

1 Week

---

## F-001 ElementId

Location:

apps/ope_core_domain/lib/ope_core/ids/

Create:

element_id.ex

Responsibilities:

- High Int64
- Low Int64
- Serialization
- Deserialization
- Comparison
- Equality

Tests:

- Create
- Compare
- Serialize
- Deserialize

---

## F-002 SequenceId

Location:

domain/ids/

Responsibilities:

- Changesets
- History
- Synchronization

Rules:

Must remain independent from ElementId.

Tests:

- Create
- Compare
- Serialize
- Deserialize

---

## F-003 RepositoryId

Location:

domain/ids/

Purpose:

Identify repositories.

Examples:

- DESIGN
- CATA
- PADD
- ISOD
- CONFIG

Tests:

- Creation
- Equality

---

## F-004 BranchId

Location:

domain/ids/

Purpose:

Identify branches.

Initial Branch:

MAIN

Tests:

- Create
- Compare

---

# Phase 2
# Value System

Goal:

Create universal value model.

Duration:

2 Weeks

---

## F-005 Boolean Value

Location:

domain/values/

Purpose:

Represent boolean values.

Tests:

- True
- False

---

## F-006 String Value

Location:

domain/values/

Purpose:

Represent strings.

Tests:

- Empty String
- Unicode String

---

## F-007 Real Value

Location:

domain/values/

Purpose:

Represent decimal numbers.

Tests:

- Positive
- Negative
- Zero

---

## F-008 Reference Value

Location:

domain/values/

Purpose:

Represent element references.

Contains:

- RepositoryId
- ElementId

Tests:

- Same Repository
- Cross Repository

---

## F-009 Array Value

Location:

domain/values/

Purpose:

Represent nested arrays.

Support:

- Mixed Types
- Nested Arrays

Tests:

- Array of Strings
- Array of Arrays
- Mixed Values

---

## F-010 Value Union

Location:

domain/values/

Purpose:

Universal value object.

Supported Types:

- Boolean
- String
- Real
- Reference
- Array

Tests:

- Type Resolution
- Validation

---

## F-011 Value Hashing

Location:

domain/values/hash/

Purpose:

Future deduplication.

Requirement:

Same value must generate same hash.

Tests:

"NORTH"

equals

"NORTH"

and both generate same hash.

---

# Phase 3
# Element Foundation

Goal:

Create engineering element model.

Duration:

2 Weeks

---

## F-012 Attribute

Location:

domain/attributes/

Contains:

- Name
- Value

Tests:

- Create
- Update
- Validate

---

## F-013 Element

Location:

domain/elements/

Contains:

- ElementId
- Class
- Attributes
- DeletedFlag

Tests:

- Create Element
- Update Attributes

---

## F-014 Name Validation

Purpose:

Prepare unique name validation.

Current:

Placeholder only.

Tests:

- Valid Name
- Empty Name

---

## F-015 Class Change Rules

Purpose:

Support:

Pipe -> Equipment

Equipment -> Structure

Rules:

Invalid attributes removed.

History preserved later.

Tests:

- Class Change
- Invalid Attribute Cleanup

---

# Phase 4
# Hierarchy Foundation

Goal:

Represent element hierarchy.

Duration:

1 Week

---

## F-016 Parent Child Relation

Location:

domain/hierarchy/

Tests:

- Link Parent
- Link Child

---

## F-017 Add Child

Tests:

- Add Child
- Validate Relationship

---

## F-018 Remove Child

Tests:

- Remove Child

---

## F-019 Move Child

Tests:

- Move Between Parents

---

## F-020 Circular Detection

Purpose:

Prevent loops.

Invalid:

A -> B -> C -> A

Tests:

- Loop Detection

---

# Phase 5
# XML Data Model

Goal:

Load engineering class definitions.

Duration:

2 Weeks

---

## F-021 XML Reader

Purpose:

Read XML files.

Tests:

- Load XML
- Invalid XML

---

## F-022 Class Loader

Purpose:

Load Classes.

Tests:

- Class Parsing

---

## F-023 Attribute Loader

Purpose:

Load Attribute Definitions.

Tests:

- Attribute Parsing

---

## F-024 Inheritance Loader

Purpose:

Support inheritance.

Tests:

- Parent Child Classes

---

## F-025 Validation Engine

Purpose:

Validate Element Creation.

Tests:

- Valid Class
- Invalid Class

---

# Phase 6
# Storage Foundation

Goal:

Introduce PostgreSQL.

Duration:

3 Weeks

---

## F-026 PostgreSQL Setup

Tasks:

- Ecto Repo
- Migrations

Tests:

- Database Connection

---

## F-027 Repository Table

Purpose:

Store repositories.

Tests:

- Insert
- Query

---

## F-028 Value Table

Purpose:

Store values.

Tests:

- Insert
- Query

---

## F-029 Element Table

Purpose:

Store elements.

Tests:

- Insert
- Read

---

## F-030 Relation Table

Purpose:

Store hierarchy.

Tests:

- Parent Child Query

---

## F-031 Repository API

Purpose:

Read and write repository data.

Tests:

- Save Element
- Load Element

---

# Phase 7
# Value Deduplication

Goal:

Store identical values once.

Duration:

2 Weeks

---

## F-032 Value Store

Purpose:

Centralized value storage.

---

## F-033 Hash Resolution

Purpose:

Lookup value by hash.

---

## F-034 Value Reuse

Purpose:

Reuse identical values.

Tests:

- Duplicate Detection
- Storage Reuse

---

# Phase 8
# Versioning Foundation

Goal:

Implement repository history engine.

Duration:

3 Weeks

---

## F-035 Changeset

Purpose:

Represent save operation.

Tests:

- Create Changeset

---

## F-036 Change Model

Types:

- Create
- Update
- Delete
- Move
- Rename

Tests:

- Each Change Type

---

## F-037 Delta Storage

Purpose:

Store changes only.

Tests:

- Delta Reconstruction

---

## F-038 Snapshot Reconstruction

Purpose:

Rebuild previous states.

Tests:

- Restore Element

---

# Phase 9
# Session Engine

Goal:

Control write access.

Duration:

1 Week

---

## F-039 Session

Features:

- Start
- Close

Tests:

- Open Session

---

## F-040 Session Validation

Purpose:

Verify active session.

Tests:

- Valid Session
- Invalid Session

---

## F-041 Close Session

Tests:

- Proper Close

---

## F-042 Session Repository

Purpose:

Persist sessions.

Tests:

- Save
- Load

---

# Phase 10
# Claim Engine

Goal:

Prevent concurrent modifications.

Duration:

2 Weeks

---

## F-043 Single Claim

Tests:

- Claim Element

---

## F-044 Multi Claim

Tests:

- Claim Multiple Elements

---

## F-045 Hierarchy Claim

Tests:

- Claim Subtree

---

## F-046 Conflict Detection

Tests:

- Overlapping Claims

---

## F-047 Release Claim

Tests:

- Release Ownership

---

# Phase 11
# SaveWork Engine

Goal:

First usable OPECore workflow.

Duration:

2 Weeks

---

## F-048 Save Workflow

Integrates:

- Session
- Claims
- Changesets

---

## F-049 Atomic Save

Purpose:

All or Nothing.

Tests:

- Successful Commit
- Forced Failure

---

## F-050 Rollback

Purpose:

Undo failed save.

Tests:

- Rollback Integrity

---

## F-051 Commit Creation

Purpose:

1 Save = 1 Changeset

Tests:

- Commit Generated

---

# Phase 12
# Synchronization Engine

Goal:

Enable distributed work.

Duration:

3 Weeks

---

## F-052 Initial Download

Purpose:

Download repository.

---

## F-053 GetChangesAfter

Purpose:

Delta Sync.

Tests:

- Retrieve Deltas

---

## F-054 Sequence Tracking

Purpose:

Track synchronization point.

---

## F-055 Sync Validation

Tests:

- Detect Missing Changes

---

# Phase 13
# History Engine

Goal:

Provide audit history.

Duration:

2 Weeks

---

## F-056 Element History

Tests:

- Element Timeline

---

## F-057 Attribute History

Tests:

- Value Evolution

---

## F-058 Hierarchy History

Tests:

- Move History

---

## F-059 Session History

Tests:

- User Activity

---

# Phase 14
# gRPC Platform

Goal:

Expose APIs.

Duration:

3 Weeks

---

## F-060 ElementService

---

## F-061 SessionService

---

## F-062 ClaimService

---

## F-063 SyncService

---

## F-064 HistoryService

Tests:

- gRPC Integration Tests

---

# Phase 15
# Multi Repository

Goal:

Support DESIGN, CATA and other repositories.

Duration:

2 Weeks

---

## F-065 Repository Management

Create repositories.

---

## F-066 Cross Repository References

Support:

DESIGN -> CATA

---

## F-067 Repository Security

Repository specific permissions.

---

# Phase 16
# Offline Workspace

Goal:

Support offline work.

Duration:

4 Weeks

---

## F-068 Workspace

Local Work Area

---

## F-069 Push Changes

Upload local modifications.

---

## F-070 Conflict Detection

Detect stale workspaces.

---

## F-071 Workspace Recovery

Recover interrupted work.

---

# Phase 17
# Branching Foundation

Goal:

Future design branch support.

Duration:

4 Weeks

---

## F-072 Create Branch

---

## F-073 Compare Branches

---

## F-074 Merge Branches

---

## F-075 Branch History

---

## F-076 Branch Sync

---

# Execution Order

Phase 0 Project Bootstrap

Phase 1 Identity Foundation

Phase 2 Value System

Phase 3 Element Foundation

Phase 4 Hierarchy Foundation

Phase 5 XML Data Model

Phase 6 Storage Foundation

Phase 7 Value Deduplication

Phase 8 Versioning Foundation

Phase 9 Session Engine

Phase 10 Claim Engine

Phase 11 SaveWork Engine

Phase 12 Synchronization Engine

Phase 13 History Engine

Phase 14 gRPC Platform

Phase 15 Multi Repository

Phase 16 Offline Workspace

Phase 17 Branching Foundation

---
