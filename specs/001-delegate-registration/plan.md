# Implementation Plan: 001-delegate-registration

**Branch**: `dev` | **Date**: 2026-04-26 | **Status**: ✅ COMPLETE  
**Input**: Full system implementation - 100% tests passing

## Summary

Build a production-ready delegate registration system for LGU MUN 2026 with per-committee roll numbers, concurrent registration safety via database locking, and committee transfer support. The system uses a monolithic FastAPI backend serving a vanilla JS/HTML/CSS frontend with premium UI/UX.

## Technical Context

**Language/Version**: Python 3.11  
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, SlowAPI (Rate Limiting), Tailwind CSS (CDN)  
**Storage**: PostgreSQL (Supabase)  
**Testing**: pytest (Backend), requests-based flow tests, Playwright (Browser)  
**Target Platform**: Render.com (Free Tier)
**Project Type**: Monolithic Web Application (FastAPI + Static Frontend)  
**Performance Goals**: Support 450+ concurrent registrations, <200ms P95 API latency  
**Constraints**: Zero build frontend, single-service architecture, database-level locking required  
**Scale/Scope**: 9 Committees, ~500 total delegates, 4 frontend pages

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Single-Service Architecture: FastAPI serves both API and static files
- ✅ Flat File Structure: `app/*.py` and `frontend/`
- ✅ Zero Build Frontend: Vanilla JS + Tailwind CDN
- ✅ Security-First: Pydantic + `SELECT FOR UPDATE` + Rate Limiting
- ✅ Constants-Driven: All magic values in `app/constants.py`
- ✅ Structured Error Responses: Standard JSON error format
- ✅ Database Locking: Implemented in all write operations
- ✅ Transfer System: MAX_TRANSFERS = 2 implemented
- ✅ Difficulty Ordering: UNSC first, hardest to easiest
- ✅ Auto-Learning: v2.0 system active

## Project Structure

### Documentation (this feature)

```text
specs/001-delegate-registration/
├── spec.md              # Requirements specification
├── plan.md              # This file (Architecture decisions)
├── tasks.md             # Implementation tasks
└── checklists/          # Process checklists
```

### Source Code (repository root)

```text
app/
├── main.py              # Routes, Middleware, App initialization
├── models.py            # SQLAlchemy models (Committee, Delegate)
├── schemas.py           # Pydantic validation schemas
├── database.py          # DB engine and session management
├── services.py          # Business logic (registration, transfer)
├── constants.py         # All magic values as constants
└── seed.py              # Idempotent database seeding

frontend/
├── index.html           # Home page
├── committees.html      # Committee listing page
├── register.html        # Registration & Transfer form
├── success.html         # Success page with confetti
├── css/                 # Local CSS files
├── js/                  # Local JS files
└── assets/              # Images, logos, photos

tests/
├── conftest.py          # Pytest configuration
├── test_api.py          # API integration tests
└── test_services.py     # Business logic unit tests

root/
├── test_full_flow.py    # Python end-to-end flow test
├── test_edge_cases.py   # Edge case verification
├── test_browser_flow.js # Playwright browser tests
└── run_tests.sh         # Automated test runner
```

**Structure Decision**: Monolithic flat architecture. FastAPI serves as the single entry point. Frontend is served as static files from the `frontend/` directory.

## Architecture Decisions

### 1. Database Locking Strategy
Used `SELECT FOR UPDATE` inside atomic transactions for both registration and transfer. This prevents multiple delegates from being assigned the same roll number or exceeding committee capacity during high concurrent load.

### 2. Roll Number Format
Per-committee sequence numbering: `LGU-[COMMITTEE_CODE]-[SEQUENCE]`.
- Example: `LGU-UNSC-001`
- Rationale: Professional look, easy to identify committee from roll number, and avoids global sequence collisions.

### 3. Transfer Logic
Implemented stateful transfers with a `transfer_count` field in the database.
- `MAX_TRANSFERS = 2`
- Transfers trigger roll number regeneration and seat count updates in both old and new committees.

### 4. UI/UX Strategy
- **Theme**: Navy/Gold premium branding.
- **Effects**: Canvas-based particle system (120 dots) and confetti.
- **Performance**: 3-second counter animations for stats to give an "alive" feel.

### 5. Learning System
Autonomous Learning System v2.0 tracks mistakes and extracts lessons to prevent repeat errors and continuously optimize the codebase.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| `SELECT FOR UPDATE` | Concurrent safety | Simple SELECT leads to race conditions at scale |
| State Management System | Tracking autonomous agents | Manual tracking is error-prone in long sessions |
| Particle System | Premium look & feel | Static background felt too "basic" for MUN branding |
