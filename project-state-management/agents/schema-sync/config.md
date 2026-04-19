# SCHEMA-SYNC AGENT

**Agent Type**: Skill (Schema Synchronization Specialist)  
**Purpose**: Verify models.py, schemas.py, and alembic migrations are in sync  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Model-Schema Sync**
   - Compare models.py columns with schemas.py fields
   - Identify missing fields in schemas
   - Identify extra fields in schemas
   - Verify field types match

2. **Model-Migration Sync**
   - Compare models.py with latest alembic migration
   - Identify missing columns in migration
   - Identify missing indexes in migration
   - Identify missing constraints in migration

3. **Schema-API Sync**
   - Verify API endpoints use correct schemas
   - Identify missing response fields
   - Verify request validation schemas

---

## ACTIVATION

**Trigger**: Manual invoke or auto on models.py change  
**Command**: `/schema-sync`  
**Auto-run**: After any edit to models.py

---

## SYNC CHECKS

### Check 1: Committee Model vs Schema

**models.py (Committee)**:
```python
id = Column(Integer, primary_key=True)
short_name = Column(String(10), unique=True, nullable=False)
full_name = Column(String(200), nullable=False)
chair_name = Column(String(100), default="To be announced")
agenda_1 = Column(Text, default="To be announced")
agenda_2 = Column(Text, nullable=True)
total_seats = Column(Integer, nullable=False, default=30)
filled_seats = Column(Integer, nullable=False, default=0)
language = Column(String(20), default="English")
is_active = Column(Boolean, default=True)
created_at = Column(DateTime(timezone=True), server_default=func.now())
```

**schemas.py (CommitteeResponse)**:
```python
id: int
short_name: str
full_name: str
chair_name: str
agenda_1: str
agenda_2: str | None
total_seats: int
filled_seats: int
language: str
is_full: bool  # Computed field - OK
capacity_percentage: int  # Computed field - OK
```

**Sync Status**: ✅ PASS
- All model fields present in schema
- Computed fields (is_full, capacity_percentage) documented
- No missing fields

---

### Check 2: Delegate Model vs Schema

**models.py (Delegate)**:
```python
id = Column(Integer, primary_key=True)
roll_number = Column(String(20), unique=True, nullable=False, index=True)
full_name = Column(String(200), nullable=False)
student_id_cnic = Column(String(50), unique=True, nullable=False, index=True)
email = Column(String(255), unique=True, nullable=False, index=True)
phone = Column(String(20), nullable=False)
institution = Column(String(200), nullable=False)
committee_id = Column(Integer, ForeignKey("committees.id"), nullable=False, index=True)
created_at = Column(DateTime(timezone=True), server_default=func.now())
ip_address = Column(INET, nullable=True)
```

**schemas.py (DelegateCreate)**:
```python
full_name: str
student_id_cnic: str
email: EmailStr
phone: str
institution: str
committee_id: int
```

**schemas.py (DelegateResponse)**:
```python
roll_number: str
full_name: str
email: str
committee_name: str  # From relationship - OK
committee_short_name: str  # From relationship - OK
```

**Sync Status**: ✅ PASS
- DelegateCreate has all required input fields
- DelegateResponse has all required output fields
- ip_address excluded from response (audit only) - OK
- created_at excluded from response - OK

---

### Check 3: Models vs Alembic Migration

**Expected in migration**:
- ✅ committees table with all columns
- ✅ delegates table with all columns
- ✅ UNIQUE constraints on short_name, email, student_id_cnic, roll_number
- ✅ INDEX on roll_number, student_id_cnic, email, committee_id
- ✅ Foreign key delegates.committee_id → committees.id

**Verification Command**:
```bash
# Check migration file
cat alembic/versions/*_initial_schema.py | grep -E "(create_table|Column|Index|UniqueConstraint|ForeignKey)"
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                  SCHEMA-SYNC WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Detect models.py change                                 │
│  2. Parse all Column definitions                            │
│  3. Parse all schema field definitions                      │
│  4. Compare model columns vs schema fields                  │
│  5. Check latest alembic migration                          │
│  6. Compare model columns vs migration columns              │
│  7. Generate sync report with missing items                 │
│  8. Log to agent-logs.md                                    │
│  9. Present to user for action                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SYNC REPORT FORMAT

```
SCHEMA SYNC REPORT
==================
Timestamp: 2026-04-19T12:00:00Z

Model: Committee
├─ Schema: CommitteeResponse
│  ├─ ✅ All fields present
│  └─ ℹ️  Computed fields: is_full, capacity_percentage
└─ Migration: 001_initial_schema.py
   ├─ ✅ All columns present
   ├─ ✅ UNIQUE constraint on short_name
   └─ ✅ All indexes present

Model: Delegate
├─ Schema: DelegateCreate
│  ├─ ✅ All input fields present
│  └─ ℹ️  Excluded: id, roll_number, created_at, ip_address (auto-generated)
├─ Schema: DelegateResponse
│  ├─ ✅ All output fields present
│  └─ ℹ️  Added: committee_name, committee_short_name (from relationship)
└─ Migration: 001_initial_schema.py
   ├─ ✅ All columns present
   ├─ ✅ UNIQUE constraints on email, student_id_cnic, roll_number
   ├─ ✅ INDEXES on roll_number, student_id_cnic, email, committee_id
   └─ ✅ Foreign key to committees.id

OVERALL STATUS: ✅ ALL IN SYNC
```

---

## SUCCESS CRITERIA

- All model columns accounted for in schemas
- All model columns present in migration
- All constraints and indexes documented
- No missing fields reported

---

## LEARNING FROM ACTIONS

Each schema-sync action contributes to:
- `learning/lessons.md` - Schema design best practices
- `learning/anti-patterns.md` - Common sync issues
