# ERROR-DEBUG AGENT

**Agent Type**: Skill (Error Debugging Specialist)  
**Purpose**: Automatic error diagnosis and fix suggestions  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Pydantic Validation Errors**
   - Detect field validation failures
   - Identify missing required fields
   - Suggest correct field types and formats
   - Provide example valid payloads

2. **SQLAlchemy Session Errors**
   - Detect session management issues
   - Identify transaction rollback needs
   - Suggest proper session handling
   - Provide session lifecycle fixes

3. **Supabase Connection Errors**
   - Detect connection string issues
   - Identify SSL/TLS problems
   - Suggest connection pool fixes
   - Provide DATABASE_URL format examples

---

## ACTIVATION

**Trigger**: Any Python traceback appears in terminal or logs  
**Auto-run**: Yes - activates on error detection  
**Manual invoke**: `/error-debug <error_message>`

---

## ERROR PATTERNS

### Pattern 1: Pydantic ValidationError
```
ValidationError: 1 validation error for DelegateCreate
  phone
    Value error, Enter a valid Pakistani phone number
```

**Diagnosis**:
- Field: phone
- Issue: Regex validation failed
- Likely cause: Wrong format (e.g., "12345" instead of "03001234567")

**Fix**:
```python
# Correct format: 11 digits starting with 03
phone = "03001234567"  # ✅ Valid
phone = "+923001234567"  # ✅ Valid with prefix
phone = "12345"  # ❌ Invalid
```

---

### Pattern 2: SQLAlchemy DetachedInstanceError
```
DetachedInstanceError: Instance <Committee at 0x...> is not bound to a Session
```

**Diagnosis**:
- Issue: Accessing object after session closed
- Likely cause: Object used outside session context

**Fix**:
```python
# ❌ Wrong
committee = db.query(Committee).first()
db.close()
print(committee.full_name)  # Error here

# ✅ Correct
committee = db.query(Committee).first()
name = committee.full_name  # Access before close
db.close()
print(name)
```

---

### Pattern 3: Supabase Connection Refused
```
OperationalError: could not connect to server: Connection refused
```

**Diagnosis**:
- Issue: Cannot reach Supabase
- Likely causes:
  1. Wrong DATABASE_URL
  2. Missing `?sslmode=require`
  3. Network/firewall issue

**Fix**:
```bash
# Check .env file
cat .env | grep DATABASE_URL

# Correct format:
DATABASE_URL=postgresql://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres?sslmode=require
#                                                                                                    ^^^^^^^^^^^^^^^^
#                                                                                                    Must have this
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                   ERROR-DEBUG WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Detect error traceback                                  │
│  2. Classify error type (Pydantic/SQLAlchemy/Supabase)     │
│  3. Extract error details (field, message, line number)    │
│  4. Match against known patterns                            │
│  5. Generate diagnosis with likely cause                    │
│  6. Provide exact fix with code examples                    │
│  7. Log to agent-logs.md                                    │
│  8. Present to user for verification                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUCCESS CRITERIA

- Error diagnosed within 30 seconds
- Fix suggestion provided with code example
- User can apply fix without additional research
- Error does not recur after fix applied

---

## LEARNING FROM ACTIONS

Each error-debug action contributes to:
- `learning/mistakes.md` - Error patterns encountered
- `learning/lessons.md` - Fix strategies that worked
- `learning/anti-patterns.md` - Common error causes
