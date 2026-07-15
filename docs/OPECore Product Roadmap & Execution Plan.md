OPECore Development Strategy

Document Version: 1.0
 Project: Open Plant Engineering Core (OPECore)
 Target Audience: Solo Developer + AI Assisted Development

Purpose

This document defines the development strategy for OPECore.

Unlike traditional enterprise development where multiple developers work simultaneously, OPECore is being built by a single developer assisted by AI.

Therefore the architecture and roadmap must prioritize:

Simplicity
Stability
Incremental development
Testability
Documentation-first approach
Feature isolation
Minimal rewrites

The goal is to allow future AI conversations to implement individual features without requiring complete project context.

AI Development Principles
Principle 1: Minimal Architecture First

Do not build for every future feature immediately.

Build only what is required for the current phase.

Bad:

Build Branching
Build Claims
Build Sync
Build Sessions
Build gRPC

Before a single Element exists.


Good:

Build ElementId

↓

Build Value System

↓

Build Element

↓

Build Hierarchy

↓

Build Storage

Principle 2: Very Small Vertical Slices

Each feature should be small.

Example:

Bad:

Build entire Repository Engine.


Good:

Build ElementId.


Next:

Build SequenceId.


Next:

Build Value Model.


Each feature must be independently completable.

Principle 3: Every Feature Must Be Testable

Every feature must contain:

Domain Logic
Unit Tests
Documentation


If a feature cannot be tested independently, it is too large.

Example:

ElementId

Create
Parse
Compare
Serialize


can be fully tested before moving forward.

Principle 4: Every Feature Must Be AI-Friendly

Before implementing a feature, create its documentation.

AI should be able to understand:

Purpose

Dependencies

Files To Modify

Tests

Interfaces

Future Extensions

Restrictions


without loading the entire repository.

Principle 5: Stable Interfaces

Once a public interface exists:

ElementId

Value

Element

Changeset


avoid changing the interface later.

Add functionality through extension rather than redesign.

Principle 6: No Future Rewrites

Avoid building temporary implementations that will later be discarded.

Example:

Bad:

Start with GUID.

Later replace with 128-bit IDs.


Good:

Start with final 128-bit IDs.


Build the foundation correctly the first time.

OPECore Layer Architecture

The system must always follow four layers.

Layer 1: Core Domain

Purpose:

Business objects and business rules.


Contains:

ElementId
SequenceId
Element
Attribute
Value
Changeset
Hierarchy


Must not know:

PostgreSQL
gRPC
Network
Ecto


Rule:

Domain knows nothing.

Layer 2: Persistence

Purpose:

Store and retrieve domain objects.


Contains:

Repositories
Mappers
Database Queries


Knows:

Domain


Does not know:

gRPC
API Layer


Rule:

Repository knows Domain.

Layer 3: Business Services

Purpose:

Workflow orchestration.


Contains:

Session Service
Claim Service
Save Service
Sync Service


Knows:

Domain
Repository


Rule:

Services know Domain + Repository.

Layer 4: gRPC

Purpose:

External communication.


Contains:

Protobuf
gRPC Services
Streaming
Authentication


Knows:

Services


Rule:

gRPC knows Services.

Build From The Center Outward
Never Build gRPC First

Wrong:

Client API
↓

Business Logic
↓

Domain


Correct:

Domain
↓

Services
↓

gRPC

Never Build PostgreSQL First

Wrong:

Create 50 Tables

Then figure out Domain.


Correct:

Domain First

Then Database.

Never Build Claiming First

Claims depend on:

Elements
Hierarchy
Sessions


Without those foundations, claims will be rewritten later.

Project Structure

Create this structure on Day 1.

ope_core/

apps/

├── ope_core_domain/
│
├── ope_core_repository/
│
├── ope_core_services/
│
├── ope_core_grpc/
│
├── ope_core_xml/
│
├── ope_core_test_support/
│
└── ope_core_app/

Dependency Rules
Domain
    ↑
Repository
    ↑
Services
    ↑
gRPC


Forbidden:

Domain -> Repository

Domain -> gRPC

Repository -> gRPC


This ensures long-term maintainability.

PHASE 0
Project Bootstrap
Duration
2-3 Days

Goal

Project compiles and tests successfully.

Nothing more.

Deliverables
Create Umbrella Project
mix new ope_core --umbrella

Configure Development Tooling
Formatter
Credo
Dialyzer
ExUnit

Configure Source Control
Git Repository
GitHub Repository
Branch Protection

Create Documentation Structure
docs/

Create ADR Folder
docs/adr/


ADR = Architecture Decision Record

Architecture Documents

Create:

docs/architecture/

001-domain.md
002-storage.md
003-grpc.md


These files become permanent project references.

Future AI conversations should refer to these files.

PHASE 1
Core IDs
Duration
1 Week

Goal

Create repository identity system.

Nothing else.

Feature 1.1
ElementId
Location
apps/ope_core_domain/lib/ids/

File
element_id.ex

Responsibilities
High Int64
Low Int64


128-bit identity.

Supported Operations
Create
Parse
Compare
Serialize
Deserialize

Tests

Location:

test/ids/


Tests:

Generate ID

Compare IDs

Serialize IDs

Deserialize IDs

Equality

Feature 1.2
SequenceId
Location
domain/ids/

Responsibilities

Used for:

Changesets

History

Synchronization

Rules

Must remain separate from:

ElementId

Example AI Prompt
Implement SequenceId in:

apps/ope_core_domain/lib/ids

Follow ElementId architecture.

Do not modify any other module.


AI now has enough information without requiring repository-wide context.

PHASE 2
Value System
Duration
2 Weeks

Goal

Create universal value model.

This is one of the most important subsystems in OPECore.

Feature 2.1
Value
Location
domain/values/

Supported Types
Boolean
String
Real
Reference
Array

Requirements

Pure domain implementation.

Must not depend on:

Database
gRPC
Ecto

Feature 2.2
ArrayValue
Goal

Support recursive arrays.

Examples:

["A", "B", "C"]

[
  true,
  false
]

[
  "PIPE",
  [
    "VALVE",
    "PUMP"
  ]
]

Tests
Array of Strings

Array of Arrays

Mixed Data Types

Deep Nested Arrays

Feature 2.3
Value Hashing
Location
domain/values/hash/

Goal

Enable future value deduplication.

Example:

"NORTH"

==

"NORTH"


must produce:

Same Hash

PHASE 3
Element Model
Duration
2 Weeks

Feature 3.1
Element
Location
domain/elements/

Fields
ElementId

Class

Attributes

DeletedFlag

Rules

No:

Database
API
Repository


Pure domain object.

Feature 3.2
Attribute Model
Location
domain/attributes/

Fields
Attribute Name

Attribute Value


Supports dynamic attributes.

Feature 3.3
Name Validation
Goal

Prepare uniqueness validation.

Currently:

Placeholder Logic


No DB integration yet.

PHASE 4
Hierarchy
Duration
1 Week

Feature 4.1
ParentChildRelation
Location
domain/hierarchy/

Operations
Add Child

Remove Child

Move Child

Rules

No:

PostgreSQL

Recursive Queries

Storage Logic


Pure hierarchy model.

PHASE 5
XML Data Model
Duration
2 Weeks

Location
ope_core_xml/

Features
Read XML

Load Classes

Load Attributes

Load Inheritance

Goal

Validate element creation against Data Model definitions.

Rules

No database.

Pure XML parsing and validation.

PHASE 6
PostgreSQL
Duration
3 Weeks

Important Rule

Database starts here.

Not earlier.

Create Only
Repositories

Elements

Relations

Values

Do NOT Create
Sessions

Claims

Changesets

History

Branches

Synchronization

Goal

Support:

Create Element

Read Element


Only.

PHASE 7
Changeset Foundation
Duration
2 Weeks

Location
domain/changesets/

Features
Create Changeset

Aggregate Changes

Commit Validation


Keep implementation minimal.

PHASE 8
Session Engine
Duration
1 Week

Location
services/sessions/

Features
Start Session

Close Session

Session Validation

Rule

Claims are not implemented yet.

PHASE 9
Claim Engine
Duration
2 Weeks

Location
services/claims/

Features
Claim Element

Claim Hierarchy

Release Claim

Scope

Server-side business logic only.

PHASE 10
Save Workflow
Duration
2 Weeks

Integrate
Session

Claims

Changeset

Workflow
Start Session

↓

Claim

↓

Modify

↓

Save

↓

Commit

↓

Release

↓

Close Session

Result

First usable OPECore version.

PHASE 11
gRPC
Duration
3 Weeks

Services
ElementService

SessionService

ClaimService

Important Rule

Build gRPC only after business logic exists.

PHASE 12
Synchronization
Duration
3 Weeks

Feature
GetChangesAfter

Goal

Delta synchronization only.

PHASE 13
Offline Workspace
Duration
4 Weeks

Features
Local Cache

Push Changes

Conflict Detection

PHASE 14
Branch Ready Refactoring
Duration
2 Weeks

Goal

Introduce:

BranchId


across repository operations.

Only:

MAIN


exists initially.

Most Important AI Rule

For every feature create a dedicated feature document.

Location:

docs/features/


Examples:

001-element-id.md

002-value-model.md

003-element.md

004-hierarchy.md

Mandatory Template For Every Feature
Feature Name

Purpose

Dependencies

Files To Change

Public Interfaces

Implementation Rules

Tests

Future Extensions

Do Not Modify

Example
Feature:
ElementId

Purpose:
128-bit repository identity.

Files:
domain/ids/element_id.ex

Tests:
test/ids/element_id_test.ex

Do Not Modify:
Value System
Hierarchy
Repository
gRPC

Golden Rule Of OPECore Development
