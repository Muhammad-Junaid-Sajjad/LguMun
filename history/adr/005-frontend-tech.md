# ADR-005: Frontend Tech & Theme

> **Scope**: Decision on frontend framework and visual identity.

- **Status:** Accepted
- **Date:** 2026-04-22
- **Feature:** Delegate Registration System
- **Context:** Need a premium-looking, fast, and mobile-responsive frontend without complex build tools.

## Decision

- **Framework**: Vanilla JS + HTML5 + CSS3
- **Styling**: Tailwind CSS (via CDN)
- **Theme**: Navy (#1e3a8a) and Gold (#f59e0b) Premium Theme
- **Animations**: Canvas particles, CSS transitions, and count-up effects.

## Consequences

### Positive

- **Zero Build**: No npm install/build needed. Just open file in browser.
- **Reliability**: Vanilla JS has no breaking version changes.
- **Performance**: Instant load times (no JS bundle to parse).
- **Visuals**: High-end animations give a professional institutional feel.

### Negative

- **Maintainability**: Harder to scale to 50+ pages without a component framework.
- **Tailwind CDN**: Requires internet connection for styling (fine for web apps).

## Alternatives Considered

- **React/Next.js**: Rejected as overkill and adding build complexity.
- **Bootstrap**: Rejected as "dated" looking; Tailwind allows for more unique institutional branding.
- **Hogwarts Theme**: Initial plan, but evolved into a more professional Navy/Gold institutional theme for LGU.

## References

- Feature Spec: [specs/001-delegate-registration/spec.md]
- Implementation Plan: [specs/001-delegate-registration/plan.md]
