#!/bin/bash
# TASK COMPLETION SIGNAL - Triggers State Manager Agent
# Call this after completing a task to notify the State Manager Agent
# Usage: ./signal-task-completion.sh "Task Name"

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
SIGNAL_FILE="$STATE_DIR/.task-completed"

TASK_NAME="${1:-Unknown Task}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Validate input
if [[ -z "$TASK_NAME" ]]; then
    echo "❌ Error: Task name required"
    echo "Usage: ./signal-task-completion.sh \"Task Name\""
    exit 1
fi

# Create signal file
echo "$TASK_NAME" > "$SIGNAL_FILE"

echo "✅ Task completion signal sent: $TASK_NAME"
echo "   Signal file: $SIGNAL_FILE"
echo "   Timestamp: $TIMESTAMP"
echo ""
echo "State Manager Agent will process this automatically..."

exit 0
