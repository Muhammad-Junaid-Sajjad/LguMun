# Pre-Launch Verification Checklist

Run this checklist before deploying to production.

## Backend Verification

- [ ] Backend server starts without errors: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- [ ] Database connection successful: Check logs for "Database connected"
- [ ] All API endpoints respond:
  - [ ] GET /api/v1/committees - Returns 9 committees
  - [ ] GET /api/v1/delegates/count - Returns delegate count
  - [ ] POST /api/v1/delegates - Returns 201 on valid registration
  - [ ] POST /api/v1/delegates/{roll}/transfer - Returns new roll number on transfer
- [ ] Rate limiting active: 5 requests per 10 minutes per IP
- [ ] Security headers present: X-Content-Type-Options, X-Frame-Options

## Frontend Verification

- [ ] All 4 pages load without errors:
  - [ ] index.html (Home page)
  - [ ] committees.html (Committee listing)
  - [ ] register.html (Registration form)
  - [ ] success.html (Success page)
- [ ] No JavaScript console errors
- [ ] Particle system visible on all 4 pages
- [ ] Stats animate with 3-second count-up
- [ ] Confetti runs on success.html
- [ ] Mobile responsive: No horizontal scroll on 375px width
- [ ] Branding: All "LGUMUN" (not "LGU MUN")

## Database Verification

- [ ] All 9 committees seeded in correct order:
      1. UNSC (UN Security Council)
      2. UNHRC (UN Human Rights Council)
      3. DISEC (UN Disarmament & International Security)
      4. UNW (UN Women)
      5. ECOSOC (Economic & Social Council)
      6. UNEP (UN Environment Programme)
      7. CCN (Climate Change Committee)
      8. JSP (Juridical Standing Committee)
      9. NCC (National Committee)
- [ ] Roll numbers generate in correct format: LGU-[CODE]-[NNN]
- [ ] Transfer counter tracks correctly (0 → 1 → 2)

## Test Suite Verification

- [ ] Unit tests pass: `pytest tests/` - Expected 27/28 (96.4%)
- [ ] Flow tests pass: `python test_full_flow.py` - Expected 5/5
- [ ] Edge case tests pass: `python test_edge_cases.py` - Expected all
- [ ] Browser tests pass: `node test_browser_flow.js` - Expected 15/15

## Production Readiness

- [ ] Database credentials in environment variables (not hardcoded)
- [ ] No DEBUG mode in production
- [ ] Error codes documented for frontend
- [ ] Rollback procedure documented
- [ ] Health check endpoint responds: GET /health

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| Developer | | | |
| QA | | | |
| Project Owner | | | |