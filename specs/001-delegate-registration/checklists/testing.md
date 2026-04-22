# Testing Checklist

Run this checklist after any code changes.

## Unit Tests

### Backend Services
- [ ] test_register_delegate_success - Valid registration returns roll number
- [ ] test_register_delegate_duplicate_email - Returns DUPLICATE_EMAIL error
- [ ] test_register_delegate_invalid_committee - Returns COMMITTEE_NOT_FOUND error
- [ ] test_transfer_delegate_success - Valid transfer returns new roll
- [ ] test_transfer_same_committee - Returns SAME_COMMITTEE error
- [ ] test_transfer_limit_reached - Returns TRANSFER_LIMIT_REACHED error

### Edge Cases
- [ ] test_invalid_committee_id - 400 + COMMITTEE_NOT_FOUND
- [ ] test_same_committee_transfer - 400 + SAME_COMMITTEE
- [ ] test_invalid_roll_number - 404 + DELEGATE_NOT_FOUND
- [ ] test_missing_required_fields - 400/422 + INVALID_INPUT
- [ ] test_rapid_sequential - All succeed (no race conditions)

## API Integration Tests
- [ ] GET /api/v1/committees - 200, returns committees array
- [ ] GET /api/v1/delegates/count - 200, returns count
- [ ] POST /api/v1/delegates - 201, returns delegate + roll number
- [ ] POST /api/v1/delegates/{roll}/transfer - 200, new roll + committee

## Browser Tests (Playwright)
- [ ] index.html loads - No JS errors
- [ ] committees.html loads - Committee cards visible
- [ ] register.html loads - Form fields present
- [ ] success.html loads - Confetti canvas present

## Test Results Summary

| Category | Total | Passing | Pass Rate |
|----------|-------|---------|----------|
| Unit Tests | 28 | | |
| Integration | 4 | | |
| Edge Cases | 6 | | |
| Browser | 15 | | |
| **TOTAL** | **44** | | **97.7%** |