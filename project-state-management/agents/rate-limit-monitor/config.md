# RATE-LIMIT-MONITOR AGENT

**Agent Type**: Subagent (Rate Limiting & Security Specialist)  
**Purpose**: Verify rate limiting works correctly  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Rate Limit Enforcement**
   - Verify 5 requests/10minute limit
   - Test 6th request returns 429
   - Verify different IPs not affected
   - Verify limit resets after 10 minutes

2. **Security Testing**
   - Test with valid payloads
   - Test with invalid payloads
   - Verify error responses correct
   - Verify no bypasses

3. **Performance Testing**
   - Measure response times
   - Verify no performance degradation
   - Check memory usage
   - Monitor for resource leaks

---

## ACTIVATION

**Trigger**: After Phase C (Backend) rate limiting added  
**Auto-run**: Manual invoke only  
**Manual invoke**: `/rate-limit-monitor`

---

## TEST SCENARIOS

### Scenario 1: Happy Path (First 5 Requests)
```bash
# Make 5 valid requests
for i in {1..5}; do
  curl -s -X POST http://localhost:8000/api/v1/delegates \
    -H "Content-Type: application/json" \
    -d '{"full_name":"Test '$i'","student_id_cnic":"TEST-'$i'","email":"test'$i'@test.com","phone":"03001234567","institution":"LGU","committee_id":1}' \
    -w "Request $i: %{http_code}\n" \
    -o /dev/null
  sleep 1
done

# Expected: All return 201 Created
```

### Scenario 2: Rate Limit Hit (6th Request)
```bash
# 6th request (should be blocked)
curl -s -X POST http://localhost:8000/api/v1/delegates \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test 6","student_id_cnic":"TEST-6","email":"test6@test.com","phone":"03001234567","institution":"LGU","committee_id":1}' \
  -w "Request 6: %{http_code}\n" \
  -o /dev/null

# Expected: 429 Too Many Requests
```

### Scenario 3: Different IP Not Affected
```bash
# Simulate different IP (using X-Forwarded-For)
curl -s -X POST http://localhost:8000/api/v1/delegates \
  -H "Content-Type: application/json" \
  -H "X-Forwarded-For: 192.168.1.100" \
  -d '{"full_name":"Different IP","student_id_cnic":"DIFF-IP","email":"diff@test.com","phone":"03001234567","institution":"LGU","committee_id":1}' \
  -w "Different IP: %{http_code}\n" \
  -o /dev/null

# Expected: 201 Created (not rate limited)
```

### Scenario 4: Limit Reset After 10 Minutes
```bash
echo "Waiting 10 minutes for rate limit reset..."
sleep 600  # 10 minutes

# Should work again
curl -s -X POST http://localhost:8000/api/v1/delegates \
  -H "Content-Type: application/json" \
  -d '{"full_name":"After Reset","student_id_cnic":"AFTER-RESET","email":"reset@test.com","phone":"03001234567","institution":"LGU","committee_id":1}' \
  -w "After reset: %{http_code}\n" \
  -o /dev/null

# Expected: 201 Created
```

---

## VERIFICATION REPORT FORMAT

```
RATE LIMIT VERIFICATION REPORT
===============================
Timestamp: 2026-04-19T12:00:00Z
Limit: 5 requests / 10 minutes / IP

Test 1: First 5 Requests
├─ Status: ✅ PASS
├─ Request 1: 201 Created ✅
├─ Request 2: 201 Created ✅
├─ Request 3: 201 Created ✅
├─ Request 4: 201 Created ✅
└─ Request 5: 201 Created ✅

Test 2: 6th Request (Limit Hit)
├─ Status: ✅ PASS
├─ HTTP Status: 429 Too Many Requests ✅
├─ Response Body: {"success":false,"error":{"code":"RATE_LIMITED","message":"Too many requests. Please wait 10 minutes and try again."}} ✅
└─ Rate limiting: WORKING ✅

Test 3: Different IP
├─ Status: ✅ PASS
├─ IP: 192.168.1.100
├─ HTTP Status: 201 Created ✅
└─ Not affected: YES ✅

Test 4: GET Endpoints (No Limit)
├─ Status: ✅ PASS
├─ GET /committees: 200 OK ✅
├─ GET /committees/1: 200 OK ✅
└─ GET /health: 200 OK ✅

Test 5: Error Messages
├─ Status: ✅ PASS
├─ 429 response: Contains error code ✅
├─ 429 response: Contains user message ✅
├─ 429 response: No stack trace ✅
└─ Envelope format: Correct ✅

OVERALL STATUS: ✅ RATE LIMITING WORKING CORRECTLY
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│            RATE-LIMIT-MONITOR WORKFLOW                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. User invokes /rate-limit-monitor                        │
│  2. Make 5 valid requests                                   │
│  3. Verify all return 201                                   │
│  4. Make 6th request                                        │
│  5. Verify returns 429                                     │
│  6. Test with different IP                                  │
│  7. Verify returns 201                                     │
│  8. Test GET endpoints                                      │
│  9. Verify no rate limiting                                │
│  10. Generate verification report                           │
│  11. Log to agent-logs.md                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUCCESS CRITERIA

- First 5 requests succeed (201)
- 6th request fails (429)
- Different IP not affected
- GET endpoints not rate limited
- Error messages user-friendly
- Limit resets after 10 minutes

---

## LEARNING FROM ACTIONS

Each rate-limit-monitor action contributes to:
- `learning/lessons.md` - Rate limiting best practices
- `learning/anti-patterns.md` - Common rate limiting issues
