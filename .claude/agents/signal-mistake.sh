#!/bin/bash
# MISTAKE SIGNAL - Triggers Learning Curator Agent
# Call this when a mistake is detected to notify the Learning Curator Agent
# Usage: ./signal-mistake.sh "Mistake Description"

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
SIGNAL_FILE="$STATE_DIR/.mistake-detected"

MISTAKE_DESC="${1:-Unknown Mistake}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Validate input
if [[ -z "$MISTAKE_DESC" ]]; then
    echo "❌ Error: Mistake description required"
    echo "Usage: ./signal-mistake.sh \"Mistake Description\""
    exit 1
fi

# Create signal file
echo "$MISTAKE_DESC" > "$SIGNAL_FILE"

echo "⚠️ Mistake signal sent: $MISTAKE_DESC"
echo "   Signal file: $SIGNAL_FILE"
echo "   Timestamp: $TIMESTAMP"
echo ""
echo "Learning Curator Agent will process this automatically..."

exit 0
