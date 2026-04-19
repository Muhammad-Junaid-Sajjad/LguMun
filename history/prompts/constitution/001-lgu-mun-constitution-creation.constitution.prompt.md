---
id: 001
title: LGU MUN Constitution Creation
stage: constitution
date: 2026-04-19
surface: agent
model: claude-sonnet-4-6
feature: lgu-mun-registration
branch: master
user: Muhammad Junaid Sajjad
command: /sp.constitution
labels: ["constitution", "architecture", "planning", "security"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - none
---

## Prompt

# /sp.constitution — LGU MUN 2026
**Version:** 1.0.0 | **Developer:** Muhammad Junaid Sajjad | **Scope:** Phase 0 only

---

## Project
Public delegate registration website for LGU MUN 2026 at Lahore Garrison University.
Hogwarts theme. Auto roll number. 9 committees. No login. No admin. No payments.

## Stack
- Backend: Python 3.11 + FastAPI (serves frontend too — one service)
- Database: PostgreSQL via Supabase free tier
- Frontend: HTML + CSS + Vanilla JS — no frameworks, no npm
- Hosting: Render.com free tier — deploys from GitHub on every push
- Assets: LGU MUN logo + past event photos live in `frontend/assets/`

## Architecture
```
app/main.py      → all routes + middleware (flat, no sub-folders)
app/models.py    → SQLAlchemy ORM: Committee + Delegate
app/schemas.py   → Pydantic validation
app/database.py  → engine + session + get_db()
app/services.py  → all business logic
app/constants.py → every magic value as a named constant
app/seed.py      → insert 9 committees (idempotent)
frontend/        → HTML + CSS + JS + assets
tests/           → pytest
```

## Non-Negotiable Rules

**Security**
- Pydantic validates ALL input server-side — client validation is UX only
- `SELECT FOR UPDATE` + atomic transaction on every registration — race condition proof
- Email stored lowercase always
- `textContent` only in JS — never `innerHTML` with user data
- Security headers on every response
- Rate limit: 5 requests / 10 min / IP via slowapi
- Zero secrets in code — environment variables only

**Code**
- All magic values in `constants.py` — never hardcoded elsewhere
- No stack traces in API responses — log internally, return clean error code
- Every error returns: `{success, error{code, message, field}, timestamp}`
- Roll number format: `LGU-MUN26-001` — defined in constants, never hardcoded

**Assets**
- `lgumun-logo.png` used as-is — no filters, no distortion, no CSS alteration
- Logo: navbar height 48px, hero height 120px, always `object-fit: contain`

## Out of Scope
Login · admin panel · email sending · payments · file uploads · country assignments.
Do not build any of these. Not even partially.

## Done When
9 committees visible → registration works → roll number assigned →
success screen shows → all tests green → live on Render URL   ; well what do you say now :

## Response snapshot

Created comprehensive LGU MUN 2026 Constitution with 6 core principles:

1. **Single-Service Architecture**: FastAPI serves both API and frontend as one service
2. **Flat File Structure**: 7 backend files in `app/`, no subdirectories
3. **Zero Build Frontend**: Vanilla HTML/CSS/JS only, no frameworks
4. **Security-First Input Handling**: Pydantic validation, SELECT FOR UPDATE, rate limiting
5. **Constants-Driven Configuration**: All magic values in `constants.py`
6. **Structured Error Responses**: Consistent JSON error format

Added sections for Stack & Architecture, Asset Handling, Scope Boundaries, Testing Requirements, and Governance. Version set to 1.0.0 with ratification date 2026-04-19.

## Outcome

- ✅ Impact: Established foundational project principles and non-negotiable rules
- 🧪 Tests: Constitution defines testing requirements but no tests created yet
- 📁 Files: Created `.specify/memory/constitution.md` with Sync Impact Report
- 🔁 Next prompts: /sp.specify to create feature specification
- 🧠 Reflection: Strong security-first approach with clear scope boundaries prevents scope creep

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Constitution covers all user requirements
- Prompt variant (if applicable): Standard constitution creation
- Next experiment (smallest change to try): Validate with actual implementation
