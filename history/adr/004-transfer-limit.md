# ADR-004: Committee Transfer Limit

> **Scope**: Policy decision on allowing delegates to change committees.

- **Status:** Accepted
- **Date:** 2026-04-22
- **Feature:** Delegate Registration System
- **Context:** Delegates often want to change committees after initial registration, but this needs to be controlled to prevent chaos.

## Decision

Implemented a stateful transfer system with a hard limit:
- **Limit**: `MAX_TRANSFERS = 2`
- **Logic**: Track `transfer_count` per delegate. On each transfer, decrement seat count from old committee, increment in new, and regenerate roll number.

## Consequences

### Positive

- **Flexibility**: Delegates can correct mistakes or change their minds.
- **Control**: Prevents "committee hopping" and keeps seat counts stable.
- **Automation**: No manual intervention needed from organizers.

### Negative

- **UI Complexity**: Requires a search-and-transfer interface.
- **Data Integrity**: Higher risk of seat count errors if logic fails (mitigated by atomic transactions).

## Alternatives Considered

- **No Transfers**: Rejected as too restrictive for a student event.
- **Unlimited Transfers**: Rejected due to logistical chaos for organizers.
- **Manual Transfers only**: Rejected as it would create a support bottleneck for the organizers.

## References

- Feature Spec: [specs/001-delegate-registration/spec.md]
- Implementation Plan: [specs/001-delegate-registration/plan.md]
