---
id: 002
title: LGU MUN Specification Creation
stage: spec
date: 2026-04-19
surface: agent
model: claude-sonnet-4-6
feature: delegate-registration
branch: 001-delegate-registration
user: Muhammad Junaid Sajjad
command: /sp.specify
labels: ["spec", "requirements", "user-stories", "api-design"]
links:
  spec: specs/001-delegate-registration/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-delegate-registration/spec.md
  - specs/001-delegate-registration/checklists/requirements.md
tests:
  - none
---

## Prompt

# /sp.specify — LGU MUN 2026 Phase 0
**Derived from:** sp.constitution | **Status:** Approved

---

## What We Are Building

4 pages. 2 API endpoints that matter. 1 database with 2 tables.

| Page | Path | Purpose |
|---|---|---|
| Homepage | `/` | Event info + CTA buttons + photo gallery + committee preview |
| Registration | `/register.html` | Form → validation → roll number |
| Success | `/success.html` | Show roll number + confirmation |
| Committees | `/committees.html` | All 9 committees + live seat availability |

---

## User Stories

**US-1 — Successful registration**
Delegate fills form, submits, gets roll number `LGU-MUN26-XXX` on success screen.
✓ Roll number shown large in gold · name, committee, email confirmed · "Save this number" message shown

**US-2 — Duplicate blocked**
Same email or same Student ID submitted again.
✓ DUPLICATE_EMAIL or DUPLICATE_ID error shown on correct field · no new DB record · email check case-insensitive

**US-3 — Full committee blocked**
Committee at capacity selected.
✓ Dropdown shows it disabled with "(FULL)" · direct POST still blocked server-side · filled_seats never exceeds total_seats

**US-4 — Committee browsing**
Visitor reads all 9 committees before registering.
✓ All 9 shown with name, chair, agenda, seats · progress bar · FULL badge · PNA shows "Urdu & English"

**US-5 — Bad input caught**
Empty fields, bad email, bad phone submitted.
✓ All errors shown at once · server validates independently of client JS

**US-6 — Race condition: last seat**
Two delegates submit simultaneously for the last seat.
✓ Exactly one succeeds · other gets COMMITTEE_FULL · filled_seats = total_seats not total_seats+1

**US-7 — Spammer blocked**
6th POST from same IP within 10 minutes.
✓ HTTP 429 returned · other IPs unaffected

---

## Functional Requirements

| ID | Requirement |
|---|---|
| FR-01 | Homepage: logo, event name/date/venue, 2 CTA buttons, photo gallery, 3 committee preview cards, footer |
| FR-02 | Registration form: Full Name, Student ID/CNIC, Email, Phone, Institution, Committee dropdown |
| FR-03 | Client-side validation: required, email format, Pakistani phone regex |
| FR-04 | Server-side Pydantic validation independent of client |
| FR-05 | Duplicate email block (case-insensitive) |
| FR-06 | Duplicate Student ID/CNIC block |
| FR-07 | Full committee block — server enforced |
| FR-08 | SELECT FOR UPDATE + atomic transaction — race condition proof |
| FR-09 | Sequential roll number: LGU-MUN26-XXX zero-padded, server-generated |
| FR-10 | Success screen: roll number (large gold), name, committee, email, save-message, 2 buttons |
| FR-11 | Committees page: live data, progress bars, FULL badges, PNA language label |
| FR-12 | Full committees disabled in dropdown (visible but unselectable) |
| FR-13 | Rate limiting: 5/10min/IP → HTTP 429 |
| FR-14 | Security headers on every response |
| FR-15 | LGU MUN logo in navbar on all 4 pages |
| FR-16 | Past event photos in homepage gallery |
| FR-17 | Hogwarts theme throughout |
| FR-18 | Responsive: 375px · 768px · 1280px |
| FR-19 | Seed script: 9 committees inserted idempotently |
| FR-20 | Health check: GET /api/v1/health |

---

## Data Models

**committees**
```
id            serial PK
short_name    varchar(10)  UNIQUE NOT NULL
full_name     varchar(200) NOT NULL
chair_name    varchar(100) DEFAULT 'To be announced'
agenda_1      text         DEFAULT 'To be announced'
agenda_2      text         NULLABLE
total_seats   integer      NOT NULL DEFAULT 30
filled_seats  integer      NOT NULL DEFAULT 0
language      varchar(20)  DEFAULT 'English'
is_active     boolean      DEFAULT true
created_at    timestamptz  DEFAULT now()
```

**delegates**
```
id               serial PK
roll_number      varchar(20)  UNIQUE NOT NULL  INDEX
full_name        varchar(200) NOT NULL
student_id_cnic  varchar(50)  UNIQUE NOT NULL  INDEX
email            varchar(255) UNIQUE NOT NULL  INDEX  — lowercase always
phone            varchar(20)  NOT NULL
institution      varchar(200) NOT NULL
committee_id     integer      FK→committees.id INDEX
created_at       timestamptz  DEFAULT now()
ip_address       inet         NULLABLE — audit only, never in API response
```

---

## API Contract

**Envelope — every response:**
```json
{ "success": true,  "data": {},    "timestamp": "..." }
{ "success": false, "error": {"code":"...","message":"...","field":"..."}, "timestamp":"..." }
```

**POST /api/v1/delegates**
Request: `full_name, student_id_cnic, email, phone, institution, committee_id`
Success 201: `roll_number, full_name, email, committee_name, committee_short_name`
Errors: 400 DUPLICATE_EMAIL · DUPLICATE_ID · COMMITTEE_FULL · COMMITTEE_NOT_FOUND · 422 · 429

**GET /api/v1/committees** — all active, with `is_full` bool + `capacity_percentage` int computed
**GET /api/v1/committees/{id}** — single · 404 if not found
**GET /api/v1/health** — always 200

---

## The 9 Committees

| short_name | full_name | language | seats |
|---|---|---|---|
| UNGA | United Nations General Assembly | English | 30 |
| UNSC | United Nations Security Council | English | 15 |
| UNHRC | United Nations Human Rights Council | English | 30 |
| ECOSOC | United Nations Economic and Social Council | English | 30 |
| WHO | World Health Organization | English | 30 |
| UNDP | United Nations Development Programme | English | 30 |
| DISEC | Disarmament and International Security Committee | English | 30 |
| UNODC | United Nations Office on Drugs and Crime | English | 30 |
| PNA | Pakistan National Assembly | Urdu & English | 30 |

---

## Constraints
- Roll numbers permanent, never reused
- Chair/agenda updated directly in Supabase dashboard — no UI needed Phase 0
- Success screen data via URL params only — no GET by roll number endpoint needed
- No email confirmation — success screen is the only confirmation
- Zero npm packages in frontend

## Edge Cases
| Situation | Behaviour |
|---|---|
| Email in CAPS | Lowercased before storage and duplicate check |
| Phone with dashes/spaces e.g. 0300-123-4567 | Strip non-numeric, then validate |
| Name with special chars: O'Brien, Arabic | Accepted as-is (UTF-8) |
| committee_id not in DB or inactive | COMMITTEE_NOT_FOUND 400 |
| total_seats = 0 | Always FULL — never selectable |
| DB drops mid-registration | Rollback · SERVER_ERROR 500 · full log internally |
| Success page opened with missing URL params | Show error: "Please register again" |
| Sequence exceeds 999 | LGU-MUN26-1000 — extends naturally, no truncation |

## Out of Scope
Login · admin · email · payments · file uploads · country assignments · PDF reports

## Success Criteria
| SC-01 | Registration under 2 min from homepage |
| SC-02 | Zero duplicate roll numbers in DB |
| SC-03 | Race condition test passes: 2 threads + 1 seat = 1 success |
| SC-04 | All 9 committees on committees page |
| SC-05 | Renders correctly on 375px mobile |
| SC-06 | pytest tests/ -v all green |
| SC-07 | Security headers on live URL via curl -I |
| SC-08 | Logo correct all 4 pages — no distortion |

## Response snapshot

Created comprehensive feature specification for LGU MUN 2026 delegate registration system:

**7 User Stories** (P1/P2 prioritized):
- Successful registration with roll number generation
- Duplicate email/ID prevention
- Committee capacity management with race condition handling
- Committee browsing with live data
- Input validation (client + server)
- Rate limiting (5/10min/IP)
- Homepage & navigation

**25 Functional Requirements** covering:
- 4 pages (homepage, registration, success, committees)
- API endpoints (POST delegates, GET committees, health check)
- Security (validation, rate limiting, headers)
- Data models (Committee, Delegate)
- Responsive design (375px, 768px, 1280px)

**10 Success Criteria** - all measurable and technology-agnostic

**Quality Checklist**: ✅ PASSED - All items verified

## Outcome

- ✅ Impact: Complete specification ready for architectural planning
- 🧪 Tests: Quality checklist passed all validation items
- 📁 Files: Created spec.md + requirements.md checklist
- 🔁 Next prompts: /sp.plan to create implementation architecture
- 🧠 Reflection: Specification is comprehensive, testable, and aligns with constitution principles

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - Specification meets all quality criteria
- Prompt variant (if applicable): Standard specification creation
- Next experiment (smallest change to try): Validate with actual implementation planning
