#!/bin/bash
# Continuous E2E Monitor - Runs every 15 minutes
# Logs results to test-results/monitor.log

TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
LOG_FILE="test-results/monitor.log"

echo "" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"
echo "E2E Monitor Run: $TIMESTAMP" >> "$LOG_FILE"
echo "=========================================" >> "$LOG_FILE"

# Run E2E test and capture output
node tests/e2e-live.js 2>&1 | tee -a "$LOG_FILE"

EXIT_CODE=${PIPESTATUS[0]}

if [ $EXIT_CODE -eq 0 ]; then
  echo "✅ Monitor run PASSED at $TIMESTAMP" >> "$LOG_FILE"
else
  echo "❌ Monitor run FAILED (exit code: $EXIT_CODE) at $TIMESTAMP" >> "$LOG_FILE"
fi

echo "---------------------------------------" >> "$LOG_FILE"