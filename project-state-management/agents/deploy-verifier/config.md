# DEPLOY-VERIFIER AGENT

**Agent Type**: Subagent (Deployment Readiness Specialist)  
**Purpose**: Pre-deployment verification checklist  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Test Verification**
   - Verify all tests pass (pytest)
   - Check test coverage > 80%
   - Verify no skipped tests
   - Verify race condition test passes

2. **Security Verification**
   - Verify security headers present
   - Verify CORS configured correctly
   - Verify rate limiting enabled
   - Verify no secrets in code

3. **Environment Verification**
   - Verify DATABASE_URL set
   - Verify ENVIRONMENT=production
   - Verify ALLOWED_ORIGINS set
   - Verify render.yaml present

4. **Database Verification**
   - Verify migrations applied
   - Verify 9 committees seeded
   - Verify no pending migrations
   - Verify schema matches models

---

## ACTIVATION

**Trigger**: Before Phase F deployment  
**Auto-run**: Manual invoke only  
**Manual invoke**: `/deploy-verifier`

---

## DEPLOYMENT CHECKLIST

### Check 1: Tests Pass
```bash
pytest tests/ -v

# Expected: All tests pass
# ===== 12 passed =====
```

### Check 2: Security Headers
```bash
curl -I http://localhost:8000/

# Expected headers:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# X-XSS-Protection: 1; mode=block
# Strict-Transport-Security: max-age=63072000
# Referrer-Policy: strict-origin-when-cross-origin
# Permissions-Policy: geolocation=(), microphone=(), camera=()
```

### Check 3: CORS Configuration
```bash
curl -H "Origin: http://localhost:3000" -I http://localhost:8000/

# Expected: Access-Control-Allow-Origin header present
```

### Check 4: Rate Limiting
```bash
# Make 6 requests in 10 minutes
for i in {1..6}; do
  curl -X POST http://localhost:8000/api/v1/delegates \
    -H "Content-Type: application/json" \
    -d '{"full_name":"Test","student_id_cnic":"TEST-'$i'","email":"test'$i'@test.com","phone":"03001234567","institution":"LGU","committee_id":1}'
  echo "Request $i"
done

# Expected: 6th request returns 429 Too Many Requests
```

### Check 5: Environment Variables
```bash
# Check .env file
cat .env | grep -E "(DATABASE_URL|ENVIRONMENT|ALLOWED_ORIGINS)"

# Expected:
# DATABASE_URL=postgresql://...
# ENVIRONMENT=production
# ALLOWED_ORIGINS=https://your-app.onrender.com
```

### Check 6: Database Migrations
```bash
alembic current

# Expected: Shows latest migration version
```

### Check 7: Committees Seeded
```bash
python -c "
from app.database import SessionLocal
from app.models import Committee

db = SessionLocal()
count = db.query(Committee).count()
print(f'Committees: {count}')
db.close()
"

# Expected: Committees: 9
```

### Check 8: No Secrets in Code
```bash
grep -r "password\|secret\|api_key\|token" app/ --include="*.py" | grep -v "# " | grep -v "PASSWORD_FIELD"

# Expected: 0 results (no hardcoded secrets)
```

---

## DEPLOYMENT REPORT FORMAT

```
DEPLOYMENT VERIFICATION REPORT
===============================
Timestamp: 2026-04-19T12:00:00Z
Target: Render.com Production

Check 1: Tests
├─ Status: ✅ PASS
├─ Total tests: 12
├─ Passed: 12
├─ Failed: 0
└─ Coverage: 85%

Check 2: Security Headers
├─ Status: ✅ PASS
├─ X-Content-Type-Options: ✅
├─ X-Frame-Options: ✅
├─ X-XSS-Protection: ✅
├─ Strict-Transport-Security: ✅
├─ Referrer-Policy: ✅
└─ Permissions-Policy: ✅

Check 3: CORS
├─ Status: ✅ PASS
├─ Allowed origins: https://your-app.onrender.com
└─ Methods: GET, POST

Check 4: Rate Limiting
├─ Status: ✅ PASS
├─ Limit: 5/10minute
├─ Test result: 6th request → 429 ✅
└─ Working: YES

Check 5: Environment
├─ Status: ✅ PASS
├─ DATABASE_URL: Set ✅
├─ ENVIRONMENT: production ✅
├─ ALLOWED_ORIGINS: Set ✅
└─ render.yaml: Present ✅

Check 6: Database
├─ Status: ✅ PASS
├─ Migrations: Applied ✅
├─ Committees: 9 ✅
├─ Delegates: 0 (fresh) ✅
└─ Schema: Matches models ✅

Check 7: Secrets
├─ Status: ✅ PASS
├─ Hardcoded secrets: 0
└─ All secrets in .env: YES

OVERALL STATUS: ✅ READY FOR DEPLOYMENT
Recommendation: PROCEED with Phase F deployment
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│              DEPLOY-VERIFIER WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. User invokes /deploy-verifier                           │
│  2. Run all tests                                           │
│  3. Check security headers                                  │
│  4. Verify CORS configuration                               │
│  5. Test rate limiting                                      │
│  6. Verify environment variables                            │
│  7. Check database migrations                               │
│  8. Verify committees seeded                                │
│  9. Scan for hardcoded secrets                              │
│  10. Generate deployment report                             │
│  11. If all pass: READY FOR DEPLOYMENT                      │
│  12. If any fail: BLOCK deployment + show issues            │
│  13. Log to agent-logs.md                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUCCESS CRITERIA

- All tests pass
- Security headers present
- CORS configured
- Rate limiting works
- Environment variables set
- Database ready
- No hardcoded secrets
- render.yaml present

---

## LEARNING FROM ACTIONS

Each deploy-verifier action contributes to:
- `learning/lessons.md` - Deployment best practices
- `learning/anti-patterns.md` - Common deployment issues
