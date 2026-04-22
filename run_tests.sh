#!/bin/bash
# Automated Test Suite Runner for LGUMUN 2026
# Runs all backend API tests and browser E2E tests

echo "=========================================="
echo "LGUMUN 2026 - AUTOMATED TEST SUITE"
echo "=========================================="
echo ""

# Check if servers are running
echo "✓ Checking server status..."
BACKEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
FRONTEND_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)

if [ "$BACKEND_STATUS" != "200" ]; then
    echo "✗ Backend not running on port 8000"
    exit 1
fi

if [ "$FRONTEND_STATUS" != "200" ]; then
    echo "✗ Frontend not running on port 3000"
    exit 1
fi

echo "✓ Backend running (port 8000)"
echo "✓ Frontend running (port 3000)"
echo ""

# Run backend API tests
echo "=========================================="
echo "BACKEND API TESTS"
echo "=========================================="
cd /home/nauman_sajjad/Desktop/LGU/Lgu-Mun
source venv/bin/activate

echo "Running pytest backend tests..."
python -m pytest tests/test_registration.py -v --tb=short 2>&1 | tee /tmp/backend_tests.log

BACKEND_RESULT=$?

echo ""
echo "=========================================="
echo "BROWSER E2E TESTS"
echo "=========================================="

echo "Installing Playwright browsers (if needed)..."
python -m playwright install chromium --with-deps > /dev/null 2>&1

echo "Running Playwright E2E tests..."
python -m pytest tests/test_browser_e2e.py -v --tb=short 2>&1 | tee /tmp/browser_tests.log

BROWSER_RESULT=$?

echo ""
echo "=========================================="
echo "TEST SUMMARY"
echo "=========================================="

# Count test results
BACKEND_PASSED=$(grep -c "PASSED" /tmp/backend_tests.log)
BACKEND_FAILED=$(grep -c "FAILED" /tmp/backend_tests.log)
BROWSER_PASSED=$(grep -c "PASSED" /tmp/browser_tests.log)
BROWSER_FAILED=$(grep -c "FAILED" /tmp/browser_tests.log)

echo ""
echo "Backend API Tests:"
echo "  ✓ Passed: $BACKEND_PASSED"
echo "  ✗ Failed: $BACKEND_FAILED"
echo ""
echo "Browser E2E Tests:"
echo "  ✓ Passed: $BROWSER_PASSED"
echo "  ✗ Failed: $BROWSER_FAILED"
echo ""

TOTAL_PASSED=$((BACKEND_PASSED + BROWSER_PASSED))
TOTAL_FAILED=$((BACKEND_FAILED + BROWSER_FAILED))

echo "Total Tests:"
echo "  ✓ Passed: $TOTAL_PASSED"
echo "  ✗ Failed: $TOTAL_FAILED"
echo ""

if [ $BACKEND_RESULT -eq 0 ] && [ $BROWSER_RESULT -eq 0 ]; then
    echo "=========================================="
    echo "✅ ALL TESTS PASSED"
    echo "=========================================="
    exit 0
else
    echo "=========================================="
    echo "❌ SOME TESTS FAILED"
    echo "=========================================="
    exit 1
fi
