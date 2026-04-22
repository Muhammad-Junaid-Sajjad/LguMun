#!/bin/bash
# SELF-EVALUATION SCRIPT - Claude evaluates its own performance
# Runs after each major task completion

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

TASK_NAME="$1"
TASK_RESULT="$2"  # success or failure

echo "========================================="
echo "CLAUDE SELF-EVALUATION"
echo "Task: $TASK_NAME"
echo "Result: $TASK_RESULT"
echo "Timestamp: $TIMESTAMP"
echo "========================================="
echo ""

# Evaluation criteria
echo "📊 EVALUATION CRITERIA:"
echo ""

# 1. Accuracy
echo "1. Accuracy: Did the task complete correctly?"
if [ "$TASK_RESULT" = "success" ]; then
    echo "   ✅ Task completed successfully"
    ACCURACY_SCORE=100
else
    echo "   ❌ Task failed or had errors"
    ACCURACY_SCORE=0
fi
echo ""

# 2. Efficiency
echo "2. Efficiency: Was the approach optimal?"
echo "   ⏱️ Check logs for unnecessary steps"
echo ""

# 3. Learning Applied
echo "3. Learning Applied: Were previous lessons used?"
LESSONS_COUNT=$(grep "^## LESSON-" "$STATE_DIR/learning/lessons.md" | wc -l)
echo "   📚 $LESSONS_COUNT lessons available"
echo ""

# 4. State Management
echo "4. State Management: Were files updated?"
LAST_UPDATE=$(grep "last_updated:" "$STATE_DIR/core/state.md" | awk '{print $2}')
echo "   📝 Last update: $LAST_UPDATE"
echo ""

# 5. Documentation
echo "5. Documentation: Was work properly logged?"
LOG_ENTRIES=$(grep "^##" "$STATE_DIR/operations/logs.md" | wc -l)
echo "   📋 $LOG_ENTRIES log entries"
echo ""

# Generate improvement suggestions
echo "========================================="
echo "💡 IMPROVEMENT SUGGESTIONS:"
echo "========================================="
echo ""

if [ "$TASK_RESULT" = "failure" ]; then
    echo "1. Analyze root cause of failure"
    echo "2. Document as MISTAKE-XXX in learning/mistakes.md"
    echo "3. Extract lesson for future prevention"
    echo "4. Apply fix and verify"
fi

echo "1. Update state files after this task"
echo "2. Log this evaluation in operations/logs.md"
echo "3. Check if new lessons should be extracted"
echo "4. Verify all changes are committed"
echo ""

# Log this evaluation
echo "## Self-Evaluation: $TASK_NAME - $TIMESTAMP" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "**Result**: $TASK_RESULT" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "**Accuracy Score**: $ACCURACY_SCORE%" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "" >> "$STATE_DIR/learning/self-improvement-loop.md"

echo "========================================="
echo "Self-evaluation complete."
echo "========================================="

exit 0
