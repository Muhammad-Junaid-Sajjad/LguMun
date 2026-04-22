# ADR-001: Backend Stack Cluster

> **Scope**: Document the decision for the core backend technology stack.

- **Status:** Accepted
- **Date:** 2026-04-22
- **Feature:** Delegate Registration System
- **Context:** Need a reliable, fast, and easy-to-deploy backend for a delegate registration system that can handle concurrent requests and serve a static frontend.

## Decision

We chose a monolithic FastAPI cluster:
- **Framework**: FastAPI (Python 3.11)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Database**: PostgreSQL (Supabase)
- **Deployment**: Render.com (Free Tier)

## Consequences

### Positive

- **Speed**: FastAPI is one of the fastest Python frameworks.
- **Developer Experience**: Automatic Swagger docs and type safety via Pydantic.
- **Simplicity**: Monolithic architecture means zero inter-service complexity.
- **Zero Cost**: Render + Supabase free tiers allow for full production deployment at no cost.

### Negative

- **Cold Starts**: Render free tier has a spinning down policy (30s+ wakeup time).
- **Concurrency Limits**: Free tier database has limited connections (Supabase).

## Alternatives Considered

- **Node.js/Express**: Rejected because FastAPI provides better validation (Pydantic) and automatic documentation out of the box.
- **Django**: Rejected as too heavy for a simple 4-page registration system.
- **Serverless (AWS Lambda)**: Rejected due to cold starts and higher setup complexity for this institution-level project.

## References

- Feature Spec: [specs/001-delegate-registration/spec.md]
- Implementation Plan: [specs/001-delegate-registration/plan.md]
