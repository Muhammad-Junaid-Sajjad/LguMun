# ADR-002: Roll Number Format

> **Scope**: Decision on the structure and generation logic of delegate roll numbers.

- **Status:** Accepted
- **Date:** 2026-04-22
- **Feature:** Delegate Registration System
- **Context:** Roll numbers need to be unique, professional, and identify the delegate's committee.

## Decision

We moved from a global sequence (`LGU-MUN26-001`) to a per-committee sequence:
- **Format**: `LGU-[COMMITTEE_CODE]-[SEQUENCE]`
- **Examples**: `LGU-UNSC-001`, `LGU-UNHRC-045`
- **Logic**: Every committee maintains its own auto-incrementing counter.

## Consequences

### Positive

- **Clarity**: Instantly know which committee a delegate belongs to.
- **Professionalism**: Matches high-end MUN standards.
- **Scalability**: Avoids a single global bottleneck for sequence generation.

### Negative

- **Complexity**: Requires tracking sequences per committee in the database.
- **Implementation**: Needs more robust service logic than a simple auto-increment ID.

## Alternatives Considered

- **Global Sequence**: `LGU-MUN26-XXX`. Rejected because it doesn't provide committee context.
- **UUID**: Rejected as unprofessional and hard for human organizers to handle on physical badges.

## References

- Feature Spec: [specs/001-delegate-registration/spec.md]
- Implementation Plan: [specs/001-delegate-registration/plan.md]
