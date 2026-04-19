# DB-GUARDIAN AGENT

**Agent Type**: Subagent (Database Integrity Specialist)  
**Purpose**: Pre-commit data integrity verification  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Seat Capacity Verification**
   - Verify filled_seats ≤ total_seats for all committees
   - Identify any committees with overflow
   - Report exact row IDs with violations

2. **Roll Number Sequence Verification**
   - Verify roll numbers are sequential (no gaps)
   - Check format: LGU-MUN26-XXX
   - Identify missing sequence numbers
   - Verify no duplicate roll numbers

3. **Data Integrity Checks**
   - Verify all delegates have valid committee_id
   - Verify all emails are lowercase
   - Verify all phone numbers match regex
   - Verify no NULL values in required fields

---

## ACTIVATION

**Trigger**: Pre-commit hook (before any git commit)  
**Auto-run**: Yes - runs automatically before commit  
**Manual invoke**: `/db-guardian`

---

## VERIFICATION QUERIES

### Check 1: Seat Capacity
```sql
SELECT 
    id, 
    short_name, 
    filled_seats, 
    total_seats,
    (filled_seats - total_seats) as overflow
FROM committees
WHERE filled_seats > total_seats;

-- Expected: 0 rows (no overflow)
```

### Check 2: Roll Number Sequence
```python
# Get all roll numbers
roll_numbers = db.query(Delegate.roll_number).order_by(Delegate.id).all()

# Extract sequence numbers
sequences = [int(rn.split('-')[-1]) for rn in roll_numbers]

# Check for gaps
expected = list(range(1, len(sequences) + 1))
gaps = set(expected) - set(sequences)

# Expected: gaps = [] (no missing numbers)
```

### Check 3: Email Lowercase
```sql
SELECT id, email
FROM delegates
WHERE email != LOWER(email);

-- Expected: 0 rows (all lowercase)
```

### Check 4: Valid Committee References
```sql
SELECT d.id, d.committee_id
FROM delegates d
LEFT JOIN committees c ON d.committee_id = c.id
WHERE c.id IS NULL;

-- Expected: 0 rows (all valid references)
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                   DB-GUARDIAN WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Triggered by git commit attempt                         │
│  2. Connect to database                                     │
│  3. Run seat capacity check                                 │
│  4. Run roll number sequence check                          │
│  5. Run email lowercase check                               │
│  6. Run committee reference check                           │
│  7. Generate integrity report                               │
│  8. If violations found: BLOCK commit + show report         │
│  9. If all pass: ALLOW commit                               │
│  10. Log to agent-logs.md                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## INTEGRITY REPORT FORMAT

```
DB INTEGRITY REPORT
===================
Timestamp: 2026-04-19T12:00:00Z
Database: Supabase Production

Check 1: Seat Capacity
├─ Status: ✅ PASS
├─ Committees checked: 9
└─ Violations: 0

Check 2: Roll Number Sequence
├─ Status: ✅ PASS
├─ Total delegates: 15
├─ Expected sequence: 1-15
├─ Actual sequence: 1-15
└─ Gaps: None

Check 3: Email Lowercase
├─ Status: ✅ PASS
├─ Emails checked: 15
└─ Violations: 0

Check 4: Committee References
├─ Status: ✅ PASS
├─ Delegates checked: 15
└─ Invalid references: 0

OVERALL STATUS: ✅ ALL CHECKS PASSED
Commit: ALLOWED
```

---

## FAILURE EXAMPLE

```
DB INTEGRITY REPORT
===================
Timestamp: 2026-04-19T12:00:00Z
Database: Supabase Production

Check 1: Seat Capacity
├─ Status: ❌ FAIL
├─ Committees checked: 9
└─ Violations: 1
    └─ Committee ID 2 (UNSC): filled_seats=16, total_seats=15, overflow=+1

Check 2: Roll Number Sequence
├─ Status: ❌ FAIL
├─ Total delegates: 15
├─ Expected sequence: 1-15
├─ Actual sequence: 1-14, 16
└─ Gaps: [15]

OVERALL STATUS: ❌ INTEGRITY VIOLATIONS FOUND
Commit: BLOCKED

ACTION REQUIRED:
1. Fix seat overflow in UNSC committee
2. Investigate missing roll number LGU-MUN26-015
3. Re-run db-guardian after fixes
```

---

## PRE-COMMIT HOOK SETUP

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

echo "Running DB Guardian checks..."

# Run db-guardian
python -c "
from app.database import SessionLocal
from app.models import Committee, Delegate

db = SessionLocal()

# Check 1: Seat capacity
overflow = db.query(Committee).filter(Committee.filled_seats > Committee.total_seats).count()
if overflow > 0:
    print('❌ FAIL: Seat capacity violations found')
    exit(1)

# Check 2: Roll number sequence
delegates = db.query(Delegate).order_by(Delegate.id).all()
sequences = [int(d.roll_number.split('-')[-1]) for d in delegates]
expected = list(range(1, len(sequences) + 1))
if sequences != expected:
    print('❌ FAIL: Roll number sequence gaps found')
    exit(1)

print('✅ PASS: All integrity checks passed')
db.close()
"

if [ $? -ne 0 ]; then
    echo "Commit blocked by DB Guardian"
    exit 1
fi
```

---

## SUCCESS CRITERIA

- All checks pass before commit allowed
- Violations reported with exact details
- User can fix issues and retry
- No false positives

---

## LEARNING FROM ACTIONS

Each db-guardian action contributes to:
- `learning/mistakes.md` - Data integrity issues found
- `learning/lessons.md` - Prevention strategies
- `learning/anti-patterns.md` - Common data corruption patterns
