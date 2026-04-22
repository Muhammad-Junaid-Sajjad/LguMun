# ADR-003: Concurrency Control Strategy

> **Scope**: Decision on handling high-volume concurrent registrations.

- **Status:** Accepted
- **Date:** 2026-04-22
- **Feature:** Delegate Registration System
- **Context:** Expecting 450+ delegates to register simultaneously, which could lead to race conditions (duplicate roll numbers or overfilled committees).

## Decision

Use database-level locking with `SELECT FOR UPDATE`:
- Wrap registration in an atomic transaction.
- Acquire an exclusive lock on the specific Committee row before reading/writing.
- Release lock only after commit.

## Consequences

### Positive

- **Integrity**: Guaranteed unique roll numbers and accurate seat counts.
- **Safety**: Prevents overselling of committees even under extreme load.

### Negative

- **Performance**: Serializes registrations for the SAME committee (others remain parallel).
- **Deadlocks**: Potential for deadlocks if not handled carefully (mitigated by only locking one resource at a time).

## Alternatives Considered

- **Application-level locks**: Rejected because they don't work across multiple server instances (if Render scales up).
- **Optimistic Locking**: Rejected as it would cause many user retries under high contention. Pessimistic locking (SELECT FOR UPDATE) is better for high-demand windows.

## References

- Feature Spec: [specs/001-delegate-registration/spec.md]
- Implementation Plan: [specs/001-delegate-registration/plan.md]
