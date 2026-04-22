#!/bin/bash
# GENERATE STATE REPORT - Creates comprehensive state update
# Called every 3 iterations by auto-learning hook

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "========================================="
echo "AUTO-MODE STATE REPORT"
echo "Generated: $TIMESTAMP"
echo "========================================="
echo ""

# 1. Current Phase
echo "📍 CURRENT PHASE:"
grep "^**Phase**:" "$STATE_DIR/core/state.md" | head -1
echo ""

# 2. Active Tasks
echo "📋 ACTIVE TASKS:"
grep "^[0-9]" "$STATE_DIR/core/state.md" | grep "⏳" | head -5
echo ""

# 3. Recent Completions
echo "✅ RECENT COMPLETIONS:"
tail -5 "$STATE_DIR/operations/logs.md" | grep "✅"
echo ""

# 4. Mistakes Logged
echo "⚠️ MISTAKES LOGGED:"
grep "^## MISTAKE-" "$STATE_DIR/learning/mistakes.md" | wc -l
echo ""

# 5. Lessons Learned
echo "📚 LESSONS LEARNED:"
grep "^## LESSON-" "$STATE_DIR/learning/lessons.md" | wc -l
echo ""

# 6. Next Actions
echo "🎯 NEXT ACTIONS:"
grep "^[0-9]" "$STATE_DIR/core/state.md" | grep "⏳" | head -3
echo ""

echo "========================================="
echo "Report complete. State files updated."
echo "========================================="

exit 0
