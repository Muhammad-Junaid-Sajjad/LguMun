#!/bin/bash
# APPLY LEARNINGS SCRIPT - Loads and applies lessons from previous sessions
# Runs at the start of each conversation

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "========================================="
echo "APPLYING LEARNINGS FROM PREVIOUS SESSIONS"
echo "Timestamp: $TIMESTAMP"
echo "========================================="
echo ""

# 1. Load all lessons
echo "📚 LOADING LESSONS:"
LESSONS_FILE="$STATE_DIR/learning/lessons.md"
LESSONS_COUNT=$(grep "^## LESSON-" "$LESSONS_FILE" | wc -l)
echo "   Found $LESSONS_COUNT lessons"
echo ""

# Display each lesson
grep "^## LESSON-" "$LESSONS_FILE" | while read -r line; do
    echo "   ✓ $line"
done
echo ""

# 2. Load all mistakes to avoid
echo "⚠️ MISTAKES TO AVOID:"
MISTAKES_FILE="$STATE_DIR/learning/mistakes.md"
MISTAKES_COUNT=$(grep "^## MISTAKE-" "$MISTAKES_FILE" | wc -l)
echo "   Found $MISTAKES_COUNT mistakes logged"
echo ""

# Display each mistake
grep "^## MISTAKE-" "$MISTAKES_FILE" | while read -r line; do
    echo "   ⚠️ $line"
done
echo ""

# 3. Load anti-patterns
echo "🚫 ANTI-PATTERNS TO AVOID:"
ANTIPATTERNS_FILE="$STATE_DIR/learning/anti-patterns.md"
ANTIPATTERNS_COUNT=$(grep "^### ANTI-PATTERN-" "$ANTIPATTERNS_FILE" | wc -l)
echo "   Found $ANTIPATTERNS_COUNT anti-patterns"
echo ""

# 4. Generate action items
echo "========================================="
echo "🎯 ACTION ITEMS FOR THIS SESSION:"
echo "========================================="
echo ""
echo "1. Apply all $LESSONS_COUNT lessons to current work"
echo "2. Avoid all $MISTAKES_COUNT documented mistakes"
echo "3. Follow best practices from anti-patterns"
echo "4. Update state files after each major task"
echo "5. Log new mistakes immediately"
echo "6. Extract new lessons as they emerge"
echo ""

# Log that learnings were applied
echo "## Learnings Applied - $TIMESTAMP" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "**Lessons Loaded**: $LESSONS_COUNT" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "**Mistakes Reviewed**: $MISTAKES_COUNT" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "**Anti-patterns Loaded**: $ANTIPATTERNS_COUNT" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "**Status**: ✅ Ready to apply in this session" >> "$STATE_DIR/learning/self-improvement-loop.md"
echo "" >> "$STATE_DIR/learning/self-improvement-loop.md"

echo "========================================="
echo "Learnings applied. Ready for work."
echo "========================================="

exit 0
