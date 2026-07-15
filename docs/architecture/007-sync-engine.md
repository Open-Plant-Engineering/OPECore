
# Synchronization Engine

Initial Sync

Client downloads:

- Hierarchy
- Elements
- Values

Stores:

LastSequence

---

Incremental Sync

Client calls:

GetChangesAfter(
    SequenceId
)

Returns:

- Created
- Deleted
- Modified
- Moved
- Claimed
- Unclaimed

Only deltas are transferred.