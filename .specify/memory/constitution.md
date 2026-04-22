<!--
Sync Impact Report:
- Version change: 1.0.0 → 2.0.0
- Modified principles: Major overhaul - added per-committee roll numbers, database locking, transfer functionality, error codes, modern frontend, Auto-mode + Learning system
- Added sections: Database Locking Strategy, Transfer System, Error Codes, Frontend Enhancements, Auto-Learning System
- Removed sections: Hogwarts-inspired theme (replaced with navy/gold premium theme)
- Templates requiring updates: ✅ Templates aligned with production-ready features
- Follow-up TODOs: Update plan.md, tasks.md, create ADRs, create PHRs, create checklists
-->

# LGU MUN 2026 Constitution

## Project Identity

**Name**: LGU MUN 2026 Delegate Registration System  
**Developer**: Muhammad Junaid Sajjad  
**Institution**: Lahore Garrison University  
**Scope**: Phase 3.7 - Production-Ready Registration System  
**Theme**: Navy/Gold Premium Theme  
**Scale**: 9 committees, no authentication, no admin panel, no payment processing

## Core Principles

### I. Single-Service Architecture
The entire application MUST be deployed as one unified service. FastAPI serves both API endpoints and static frontend files. No microservices, no separate frontend server, no build tools. This ensures zero deployment complexity and maximum reliability on free-tier hosting.

**Rationale**: Free-tier hosting (Render.com) has resource limits. A monolithic approach minimizes memory overhead, eliminates inter-service communication failures, and simplifies deployment to a single GitHub push.

### II. Flat File Structure
All backend code MUST live in `app/*.py` with no subdirectories. Frontend MUST live in `frontend/` with assets in `frontend/assets/`. No nested modules, no complex imports.

**Structure**:
```
app/main.py      → all routes + middleware
app/models.py    → SQLAlchemy ORM: Committee + Delegate
app/schemas.py   → Pydantic validation
app/database.py  → engine + session + get_db()
app/services.py  → all business logic
app/constants.py → every magic value as a named constant
app/seed.py      → insert 9 committees (idempotent)
frontend/        → HTML + CSS + JS + assets
tests/           → pytest
```

**Rationale**: Simplicity over abstraction. With only 7 backend files, navigation is instant and mental overhead is minimal. No time wasted on "where does this go?"

### III. Zero Build Frontend
Frontend MUST use vanilla HTML, CSS, and JavaScript only. No React, Vue, npm, webpack, or any build step. Assets live in `frontend/assets/` and are served directly by FastAPI. Tailwind CSS via CDN is permitted for rapid styling.

**Rationale**: Build tools add complexity, deployment friction, and failure points. Vanilla JS + Tailwind CDN is sufficient for a registration form and committee display. Eliminates 10+ minutes of build time and npm dependency vulnerabilities.

### IV. Security-First Input Handling
- Pydantic MUST validate ALL input server-side — client validation is UX only
- `SELECT FOR UPDATE` + atomic transaction MUST wrap every registration to prevent race conditions
- Email MUST be stored lowercase always
- JavaScript MUST use `textContent` only — never `innerHTML` with user data
- Security headers MUST be present on every response
- Rate limiting MUST be enforced: 5 requests / 10 min / IP via slowapi
- Zero secrets in code — environment variables only

**Rationale**: Registration systems are high-value targets for spam and duplicate entries. Race conditions on roll number assignment would cause catastrophic UX failures. XSS vulnerabilities would compromise delegate data.

### V. Constants-Driven Configuration
Every magic value MUST be defined in `app/constants.py` and imported elsewhere. Never hardcode strings, numbers, formats, or limits in business logic.

**Examples**:
- Roll number format: `LGU-UNSC-001` (per-committee)
- Rate limit thresholds
- Committee names and capacities
- Transfer limit: MAX_TRANSFERS = 2
- Error codes and messages

**Rationale**: Changing "LGU" prefix or committee codes next year should be a one-line edit, not a grep-and-replace hunt. Constants serve as living documentation of all configurable values.

### VI. Structured Error Responses
Every error MUST return JSON in this exact format:
```json
{
  "success": false,
  "error": {
    "code": "DUPLICATE_EMAIL",
    "message": "This email is already registered",
    "field": "email"
  },
  "timestamp": "2026-04-19T09:00:00Z"
}
```

No stack traces in API responses. Log internally, return clean error codes.

**Rationale**: Frontend needs machine-readable error codes to display localized messages and highlight specific form fields. Stack traces leak implementation details and confuse users.

### VII. Database Locking Strategy
Every registration and transfer operation MUST use database-level locking with `SELECT FOR UPDATE` to prevent race conditions under concurrent load.

**Implementation**:
```python
# Acquire lock on committee row
committee = db.query(Committee).filter(Committee.id == committee_id).with_for_update().first()
# Process registration
# Commit releases lock
```

**Rationale**: At 450+ concurrent registrations, simple SELECT queries cause race conditions. Database-level locking is the only way to guarantee unique roll numbers and accurate seat counts.

### VIII. Transfer System
Delegates MUST be able to transfer committees up to MAX_TRANSFERS times (current: 2). Each transfer regenerates the roll number for the new committee.

**Rules**:
- Cannot transfer to same committee (SAME_COMMITTEE error)
- Cannot transfer if limit reached (TRANSFER_LIMIT_REACHED error)
- Cannot transfer to full committee (COMMITTEE_FULL error)
- Roll number regenerates on each transfer

**Rationale**: Real-world scenarios require flexibility. 2 transfers is enough for most delegate scenarios while preventing abuse.

### IX. Committee Difficulty Ordering
Committees MUST be ordered by difficulty (hardest first) in the seeding and display:
1. UNSC (UN Security Council) - Hardest
2. UNHRC (UN Human Rights Council)
3. DISEC (UN Disarmament & International Security)
4. UNW (UN Women)
5. ECOSOC (Economic & Social Council)
6. UNEP (UN Environment Programme)
7. CCN (Climate Change Committee)
8. JSP (Juridical Standing Committee)
9. NCC (National Committee)

**Rationale**: Hardest committees require experienced delegates. Ordering helps delegates make informed choices.

### X. Auto-Learning System
Project MUST include autonomous learning system with:
- Mistake tracking and root cause analysis
- Lesson extraction and prevention rules
- Anti-pattern identification
- Continuous improvement metrics

**Files**:
- `project-state-management/learning/self-improvement-loop.md`
- Auto-mode configuration in `.claude/auto-mode-config.md`

**Rationale**: System should learn from every mistake and continuously improve. No repeat mistakes.

## Stack & Architecture

### Technology Choices
- **Backend**: Python 3.11 + FastAPI
- **Database**: PostgreSQL via Supabase free tier
- **Frontend**: HTML + CSS + Vanilla JS + Tailwind CSS (CDN)
- **Hosting**: Render.com free tier (deploys from GitHub on every push)
- **Testing**: pytest

### Database Schema
Two tables only:
1. **Committee**: id, name, short_name, description, capacity, difficulty_order
2. **Delegate**: id, roll_number, full_name, email, phone, institution, student_id_cnic, committee_id, transfer_count, registered_at

### Deployment Pipeline
GitHub push → Render.com auto-deploy → Database migrations run → Service restarts → Health check passes

## Asset Handling

### Logo Usage Rules
- `lgumun-logo.png` MUST be used as-is — no filters, no distortion, no CSS alteration
- Navbar: height 48px, `object-fit: contain`
- Hero section: height 120px, `object-fit: contain`
- Always maintain aspect ratio
- Dual logo: LGU Official + LGUMUN Society

**Rationale**: Brand consistency is non-negotiable. CSS filters or distortions would violate university branding guidelines.

### Past Event Photos
Live in `frontend/assets/` and are served directly. No CDN, no external hosting.

## Scope Boundaries

### Explicitly Out of Scope
The following features MUST NOT be built, even partially:
- User login/authentication
- Admin panel or dashboard
- Email sending (confirmation, reminders, etc.)
- Payment processing
- File uploads (resumes, photos, etc.)
- Country/position assignments
- Delegate editing or cancellation (except transfer)

**Rationale**: Phase 3.7 is registration only with basic transfer support. These features would triple development time and introduce security/compliance complexity beyond current requirements.

## Testing Requirements

### Test Coverage Mandate
- Every service function MUST have a unit test
- Every API endpoint MUST have an integration test
- Race condition scenarios MUST be tested with concurrent requests
- All tests MUST pass before deployment

### Test Categories
1. **Unit tests**: `services.py` business logic
2. **Integration tests**: API endpoints with real database transactions
3. **Concurrency tests**: Parallel registration attempts with same email
4. **Edge case tests**: Invalid inputs, full committees, transfer limits

## Frontend Enhancements

### Required UI Features
- Particle system with 120 floating glowing dots on all pages
- Smooth animations: fadeInUp, scaleIn, float
- Real-time stats with 3-second count-up animations
- Confetti celebration on success page (runs forever)
- YouTube video modal in Past Events page
- Mobile-responsive design

### Branding
- All "LGU MUN" → "LGUMUN" (unified branding)
- Navy (#1e3a8a) + Gold (#f59e0b) theme
- Professional button hover effects
- Logo glow animations

## Error Codes

Must implement these error codes:

| Code | Message | Trigger |
|------|---------|--------|
| DUPLICATE_EMAIL | Email already registered | Duplicate registration |
| COMMITTEE_NOT_FOUND | Committee not found | Invalid committee ID |
| COMMITTEE_FULL | Committee is full | Capacity reached |
| SAME_COMMITTEE | Already in this committee | Transfer to same committee |
| CAN_TRANSFER | Cannot transfer | Transfer not allowed |
| TRANSFER_LIMIT_REACHED | Transfer limit reached | More than 2 transfers |
| DELEGATE_NOT_FOUND | Delegate not found | Invalid roll number |
| INVALID_INPUT | Invalid input | Validation error |

## Governance

### Amendment Process
1. Propose change with rationale in GitHub issue
2. Update constitution with version bump (see versioning rules below)
3. Update affected templates in `.specify/templates/`
4. Document in Sync Impact Report (HTML comment at top of this file)
5. Commit with message: `docs: amend constitution to vX.Y.Z (summary)`

### Versioning Rules
- **MAJOR**: Backward incompatible changes (e.g., removing a principle, changing stack)
- **MINOR**: New principle added or materially expanded guidance
- **PATCH**: Clarifications, wording fixes, typo corrections

### Compliance Verification
- All PRs MUST verify compliance with this constitution
- Any deviation MUST be justified in PR description and approved by project owner
- Constitution supersedes all other practices

### Runtime Guidance
For agent-specific development guidance, refer to `CLAUDE.md` in project root.

---

**Version**: 2.0.0 | **Ratified**: 2026-04-22 | **Last Amended**: 2026-04-22