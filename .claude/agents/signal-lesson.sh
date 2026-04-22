#!/bin/bash
# LESSON SIGNAL - Triggers Learning Curator Agent
# Call this when a lesson is learned to notify the Learning Curator Agent
# Usage: ./signal-lesson.sh "Lesson Description"

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
SIGNAL_FILE="$STATE_DIR/.lesson-detected"

LESSON_DESC="${1:-Unknown Lesson}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Validate input
if [[ -z "$LESSON_DESC" ]]; then
    echo "❌ Error: Lesson description required"
    echo "Usage: ./signal-lesson.sh \"Lesson Description\""
    exit 1
fi

# Create signal file
echo "$LESSON_DESC" > "$SIGNAL_FILE"

echo "📚 Lesson signal sent: $LESSON_DESC"
echo "   Signal file: $SIGNAL_FILE"
echo "   Timestamp: $TIMESTAMP"
echo ""
echo "Learning Curator Agent will process this automatically..."

exit 0
