# API-TEST AGENT

**Agent Type**: Skill (API Testing Specialist)  
**Purpose**: Generate curl commands for API endpoint testing  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Happy Path Tests**
   - Generate valid request payloads
   - Provide expected 200/201 responses
   - Include all required fields

2. **Duplicate Case Tests**
   - Generate duplicate email scenarios
   - Generate duplicate student ID scenarios
   - Provide expected 400 error responses

3. **Invalid Input Tests**
   - Generate missing field scenarios
   - Generate invalid format scenarios
   - Provide expected 422 validation errors

---

## ACTIVATION

**Trigger**: Manual invoke only  
**Command**: `/api-test <route_name>`  
**Example**: `/api-test POST /api/v1/delegates`

---

## TEST TEMPLATES

### POST /api/v1/delegates

#### Happy Path
```bash
curl -s -X POST http://localhost:8000/api/v1/delegates \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ali Hassan",
    "student_id_cnic": "LGU-2023-001",
    "email": "ali@test.com",
    "phone": "03001234567",
    "institution": "Lahore Garrison University",
    "committee_id": 1
  }' | python3 -m json.tool

# Expected: 201 Created
# {
#   "success": true,
#   "data": {
#     "roll_number": "LGU-MUN26-001",
#     "full_name": "Ali Hassan",
#     "email": "ali@test.com",
#     "committee_name": "United Nations General Assembly",
#     "committee_short_name": "UNGA"
#   },
#   "timestamp": "2026-04-19T12:00:00Z"
# }
```

#### Duplicate Email
```bash
curl -s -X POST http://localhost:8000/api/v1/delegates \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Different Person",
    "student_id_cnic": "LGU-2023-002",
    "email": "ali@test.com",
    "phone": "03001234568",
    "institution": "Lahore Garrison University",
    "committee_id": 1
  }' | python3 -m json.tool

# Expected: 400 Bad Request
# {
#   "success": false,
#   "error": {
#     "code": "DUPLICATE_EMAIL",
#     "message": "This email is already registered.",
#     "field": "email"
#   },
#   "timestamp": "2026-04-19T12:00:00Z"
# }
```

#### Invalid Phone
```bash
curl -s -X POST http://localhost:8000/api/v1/delegates \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Bad Phone",
    "student_id_cnic": "LGU-2023-003",
    "email": "badphone@test.com",
    "phone": "12345",
    "institution": "Lahore Garrison University",
    "committee_id": 1
  }' | python3 -m json.tool

# Expected: 422 Unprocessable Entity
# {
#   "detail": [
#     {
#       "type": "value_error",
#       "loc": ["body", "phone"],
#       "msg": "Value error, Enter a valid Pakistani phone number (e.g. 03001234567)"
#     }
#   ]
# }
```

---

### GET /api/v1/committees

#### Happy Path
```bash
curl -s http://localhost:8000/api/v1/committees | python3 -m json.tool

# Expected: 200 OK
# {
#   "success": true,
#   "data": {
#     "committees": [
#       {
#         "id": 1,
#         "short_name": "UNGA",
#         "full_name": "United Nations General Assembly",
#         "chair_name": "To be announced",
#         "agenda_1": "To be announced",
#         "agenda_2": null,
#         "total_seats": 30,
#         "filled_seats": 0,
#         "language": "English",
#         "is_full": false,
#         "capacity_percentage": 0
#       }
#     ]
#   },
#   "timestamp": "2026-04-19T12:00:00Z"
# }
```

---

### GET /api/v1/committees/{id}

#### Happy Path
```bash
curl -s http://localhost:8000/api/v1/committees/1 | python3 -m json.tool

# Expected: 200 OK (same structure as above, single committee)
```

#### Not Found
```bash
curl -s http://localhost:8000/api/v1/committees/999 | python3 -m json.tool

# Expected: 404 Not Found
# {
#   "success": false,
#   "error": {
#     "code": "NOT_FOUND",
#     "message": "Committee not found.",
#     "field": null
#   },
#   "timestamp": "2026-04-19T12:00:00Z"
# }
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                    API-TEST WORKFLOW                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Receive route name (e.g., POST /delegates)             │
│  2. Load test template for that route                       │
│  3. Generate happy path curl command                        │
│  4. Generate duplicate case curl command                    │
│  5. Generate invalid input curl command                     │
│  6. Include expected responses for each                     │
│  7. Log to agent-logs.md                                    │
│  8. Present to user for execution                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUCCESS CRITERIA

- All 3 test cases generated (happy, duplicate, invalid)
- Expected responses documented
- User can copy-paste and run immediately
- Tests cover all user stories

---

## LEARNING FROM ACTIONS

Each api-test action contributes to:
- `learning/lessons.md` - API testing best practices
- Test coverage tracking
