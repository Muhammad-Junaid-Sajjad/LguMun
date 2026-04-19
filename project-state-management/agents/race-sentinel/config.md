# RACE-SENTINEL AGENT

**Agent Type**: Subagent (Concurrency & Race Condition Specialist)  
**Purpose**: Verify race condition protection in register_delegate()  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **SELECT FOR UPDATE Verification**
   - Verify `with_for_update()` present on committee query
   - Ensure lock acquired before capacity check
   - Verify lock held until commit

2. **Transaction Integrity**
   - Verify filled_seats increment in same transaction
   - Verify INSERT delegate in same transaction
   - Verify commit happens after both operations
   - Verify rollback on any error

3. **Concurrency Testing**
   - Simulate 2 concurrent requests for last seat
   - Verify exactly 1 succeeds, 1 fails
   - Verify filled_seats = total_seats (not +1)
   - Verify no duplicate roll numbers

---

## ACTIVATION

**Trigger**: Any edit to services.py register_delegate()  
**Auto-run**: Yes - runs after function changes  
**Manual invoke**: `/race-sentinel`

---

## CRITICAL CODE PATTERNS

### Pattern 1: SELECT FOR UPDATE (REQUIRED)
```python
# ✅ CORRECT - Lock acquired
committee = (
    db.query(Committee)
    .filter(Committee.id == data.committee_id)
    .with_for_update()  # ← CRITICAL: Must be present
    .first()
)

# ❌ WRONG - No lock
committee = db.query(Committee).filter(Committee.id == data.committee_id).first()
```

### Pattern 2: Atomic Transaction (REQUIRED)
```python
# ✅ CORRECT - All in one transaction
try:
    # Step 1: Lock committee
    committee = db.query(Committee).with_for_update().first()
    
    # Step 2: Check capacity
    if committee.filled_seats >= committee.total_seats:
        raise AppException("COMMITTEE_FULL", ...)
    
    # Step 3: Create delegate
    delegate = Delegate(...)
    db.add(delegate)
    
    # Step 4: Increment seats
    committee.filled_seats += 1
    
    # Step 5: Commit (all or nothing)
    db.commit()
except Exception:
    db.rollback()  # ← CRITICAL: Rollback on any error
    raise

# ❌ WRONG - Multiple transactions
committee = db.query(Committee).first()
if committee.filled_seats >= committee.total_seats:
    raise AppException("COMMITTEE_FULL", ...)
db.commit()  # ← Commit too early

delegate = Delegate(...)
db.add(delegate)
committee.filled_seats += 1
db.commit()  # ← Second commit - race condition window
```

### Pattern 3: Rollback on Error (REQUIRED)
```python
# ✅ CORRECT - Rollback on error
try:
    # ... operations ...
    db.commit()
except AppException:
    db.rollback()
    raise
except Exception as e:
    db.rollback()
    logger.error(f"Error: {e}")
    raise AppException("SERVER_ERROR", ...)

# ❌ WRONG - No rollback
try:
    # ... operations ...
    db.commit()
except Exception as e:
    logger.error(f"Error: {e}")
    raise  # ← Commit may have partially succeeded
```

---

## VERIFICATION QUERIES

### Query 1: Check SELECT FOR UPDATE Present
```bash
grep -n "with_for_update" app/services.py

# Expected: 1 match in register_delegate()
```

### Query 2: Check Transaction Structure
```bash
grep -A 30 "def register_delegate" app/services.py | grep -E "(try:|except|db.commit|db.rollback)"

# Expected:
# - try: present
# - db.commit() inside try
# - db.rollback() in except
```

### Query 3: Check Increment in Transaction
```bash
grep -A 50 "def register_delegate" app/services.py | grep -E "(filled_seats|db.commit)"

# Expected:
# - filled_seats += 1 before db.commit()
# - No operations after db.commit()
```

---

## VERIFICATION REPORT FORMAT

```
RACE-SENTINEL VERIFICATION REPORT
==================================
Timestamp: 2026-04-19T12:00:00Z
Function: register_delegate() in app/services.py

Check 1: SELECT FOR UPDATE
├─ Status: ✅ PASS
├─ Location: Line 45
├─ Code: committee = db.query(Committee).with_for_update().first()
└─ Lock acquired: YES

Check 2: Transaction Integrity
├─ Status: ✅ PASS
├─ Try block: Present (Line 40)
├─ Except block: Present (Line 65)
├─ db.commit(): Line 62 (inside try)
├─ db.rollback(): Line 65 (inside except)
└─ All operations atomic: YES

Check 3: Increment in Transaction
├─ Status: ✅ PASS
├─ filled_seats += 1: Line 60
├─ db.commit(): Line 62
├─ Operations after commit: None
└─ Atomic: YES

Check 4: Concurrent Test
├─ Status: ✅ PASS
├─ Test: 2 threads, 1 seat
├─ Result: 1 success, 1 COMMITTEE_FULL
├─ filled_seats: 1 (not 2)
└─ Race condition: PREVENTED

OVERALL STATUS: ✅ RACE CONDITION PROTECTION VERIFIED
```

---

## FAILURE EXAMPLE

```
RACE-SENTINEL VERIFICATION REPORT
==================================
Timestamp: 2026-04-19T12:00:00Z
Function: register_delegate() in app/services.py

Check 1: SELECT FOR UPDATE
├─ Status: ❌ FAIL
├─ Location: Line 45
├─ Code: committee = db.query(Committee).first()
└─ Lock acquired: NO ← CRITICAL: with_for_update() missing

OVERALL STATUS: ❌ RACE CONDITION PROTECTION MISSING
Action: REFUSE COMMIT

ERROR MESSAGE:
"Race condition vulnerability detected in register_delegate():
- SELECT FOR UPDATE not present
- Multiple threads can read same committee state
- filled_seats can exceed total_seats
- Duplicate roll numbers possible

FIX REQUIRED:
Change line 45 from:
  committee = db.query(Committee).filter(...).first()
To:
  committee = db.query(Committee).filter(...).with_for_update().first()

This acquires a database lock preventing concurrent modifications."
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                 RACE-SENTINEL WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Detect edit to services.py                              │
│  2. Parse register_delegate() function                      │
│  3. Check for with_for_update() call                        │
│  4. Verify transaction structure (try/except)               │
│  5. Verify filled_seats increment in transaction            │
│  6. Verify db.commit() after increment                      │
│  7. Verify db.rollback() in except                          │
│  8. Run concurrent test (2 threads, 1 seat)                 │
│  9. Generate verification report                            │
│  10. If violations: BLOCK commit + show error               │
│  11. If all pass: ALLOW commit                              │
│  12. Log to agent-logs.md                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUCCESS CRITERIA

- SELECT FOR UPDATE present and correct
- Transaction structure sound (try/except/commit/rollback)
- filled_seats increment inside transaction
- Concurrent test passes (1 success, 1 failure)
- No race condition window exists

---

## LEARNING FROM ACTIONS

Each race-sentinel action contributes to:
- `learning/mistakes.md` - Concurrency issues found
- `learning/lessons.md` - Transaction best practices
- `learning/anti-patterns.md` - Common race condition patterns
