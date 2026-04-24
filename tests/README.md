# LGU MUN 2026 - Testing Guide

## Overview
This project implements a comprehensive testing strategy following TDD principles.

## Test Layers

### Layer 1: Unit Tests (test_logic.py)
Tests business logic in isolation using pytest.

**What it tests:**
- Committee 50-seat limit
- 2-switch transfer limit
- Roll number uniqueness
- Email duplicate rejection
- Atomic transactions

**Run:**
```bash
pytest tests/test_logic.py -v
```

---

### Layer 2: API Tests (test_registration.py, test_admin.py)
Tests API endpoints directly.

**What it tests:**
- Registration endpoint
- Transfer endpoint
- Admin endpoints with API key
- Settings CRUD

**Run:**
```bash
pytest tests/test_registration.py -v
pytest tests/test_admin.py -v
```

---

### Layer 3: E2E Tests (tests/e2e.spec.js)
End-to-end tests using Playwright.

**What it tests:**
- Full browser-to-DB flow
- Registration form submission
- Committee switch limits (3rd rejected)
- Race conditions
- Admin authentication

**Run:**
```bash
npx playwright test tests/e2e.spec.js
```

---

### Layer 4: Load Tests (tests/load-test.js)
Load testing using k6.

**What it tests:**
- 450 concurrent users
- Response time under load
- Error rate monitoring

**Run:**
```bash
k6 run tests/load-test.js
```

---

## Test Scenarios

### 1. Committee Switch Limit
- **Rule:** 2 switches allowed, 3rd rejected
- **Test:**
  ```javascript
  // E2E: e2e.spec.js
  test('should reject 3rd committee switch attempt')
  ```

### 2. Seat Limit (50 per committee)
- **Rule:** Max 50 delegates per committee
- **Test:**
  ```javascript
  // Load: load-test.js
  test('should respect 50 seats per committee')
  ```

### 3. Concurrent Registrations
- **Rule:** Handle 450 simultaneous
- **Test:**
  ```javascript
  // Load: load-test.js
  // 450 concurrent users
  ```

### 4. 2-Hour Cutoff
- **Rule:** Switch disabled 2 hours before event
- **Implementation:** Settings check in settings.js

### 5. Data Flush (48h)
- **Rule:** Data flushed 48h after event
- **Implementation:** Manual cleanup or cron

---

## Running All Tests

### Quick Test (API)
```bash
# Test all endpoints
curl http://localhost:8000/api/v1/health
curl http://localhost:8000/api/v1/committees
curl -H "X-Admin-API-Key: lgumun2026_admin_secure_key_x9y2z" \
  http://localhost:8000/api/v1/admin/stats
```

### Full Test Suite
```bash
# 1. Unit tests
pytest tests/test_logic.py

# 2. API tests
pytest tests/test_registration.py
pytest tests/test_admin.py

# 3. E2E tests (requires browser)
npx playwright test tests/e2e.spec.js

# 4. Load tests (requires k6)
k6 run tests/load-test.js
```

---

## Test Frequency

| Test Type | Frequency | Trigger |
|----------|----------|----------|
| API Tests | Every commit | Pre-commit hook |
| E2E Tests | Daily | CI/CD |
| Load Tests | Weekly | Before event |

---

## Key Test Files

| File | Purpose |
|------|---------|
| `tests/test_logic.py` | Business logic (TDD) |
| `tests/test_registration.py` | Registration API |
| `tests/test_admin.py` | Admin API |
| `tests/e2e.spec.js` | Playwright E2E |
| `tests/load-test.js` | k6 Load testing |
| `tests/conftest.py` | pytest fixtures |

---

## Test Metrics

| Metric | Target |
|--------|--------|
| Test Coverage | 90%+ |
| API Response Time | <200ms p95 |
| Max Concurrent | 450 |
| Error Rate | <5% |
| Seat Limit | 50 per committee |
| Transfer Limit | 2 per delegate |