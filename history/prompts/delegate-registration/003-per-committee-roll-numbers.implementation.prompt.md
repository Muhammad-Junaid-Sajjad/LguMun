---
id: 003
title: Per-Committee Roll Number Implementation
stage: implementation
date: 2026-04-22
surface: agent
model: claude-4-sonnet
feature: delegate-registration
branch: dev
user: Muhammad Junaid Sajjad
command: Implement per-committee roll number generation
labels: [backend, database, roll-number]
files:
  - app/services.py (register_delegate function)
  - app/constants.py (ROLL_PREFIX)
  - app/models.py (Delegate model)
tests:
  - test_full_flow.py (registration flow test)
spec: specs/001-delegate-registration/spec.md
plan: specs/001-delegate-registration/plan.md
adr: history/adr/002-roll-number-format.md
pr: null
---

## Prompt

Implement per-committee roll number generation so that delegates get roll numbers like LGU-UNSC-001, LGU-UNHRC-045, etc. Each committee should have its own counter.

## Response snapshot

Implemented `register_delegate` function in app/services.py that queries the Committee table to find the highest existing roll number for that committee, then adds 1. Uses `SELECT FOR UPDATE` to lock the committee row during registration to prevent race conditions under concurrent load.

## Outcome

- ✅ Impact: Delegates can now identify their committee from their roll number
- 🧪 Tests: 5/5 flow tests passing, edge case tests passing
- 📁 Files: Modified app/services.py, app/constants.py
- 🔁 Next prompts: Implement transfer functionality
- 🧠 Reflection: Per-committee format is more professional than global sequence

## Evaluation notes (flywheel)

- Failure modes observed: None yet for roll numbers
- Graders run and results (PASS/FAIL): 5/5 tests PASS
- Prompt variant (if applicable): None
- Next experiment (smallest change to try): Add committee code shorthand to constants