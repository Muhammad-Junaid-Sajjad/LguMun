#!/bin/bash
# AUTO-STARTUP SCRIPT FOR LGU MUN 2026 PROJECT
# This script runs automatically when Claude Code starts in this directory

echo "========================================="
echo "LGU MUN 2026 - AUTO-MODE STARTUP"
echo "========================================="
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo "Branch: $(git branch --show-current)"
echo ""

# 1. Check project state management system
echo "1. Checking project-state-management system..."
if [ -f "project-state-management/core/state.md" ]; then
    echo "   ✅ State management system found"
    AUTO_MODE=$(grep -q "auto_mode: FULLY_ACTIVATED" project-state-management/core/state.md && echo "FULLY ACTIVATED" || echo "INACTIVE")
    echo "   Auto-Mode Status: $AUTO_MODE"
else
    echo "   ⚠️ State management system not found"
fi

# 2. Check git status
echo ""
echo "2. Checking git status..."
git status --short
echo "   Branch: $(git branch --show-current)"
echo "   Ahead of origin: $(git rev-list --count origin/dev..dev 2>/dev/null || echo "0") commits"

# 3. Check for pending tasks
echo ""
echo "3. Checking pending tasks..."
if [ -f "project-state-management/operations/tasks.md" ]; then
    PENDING_TASKS=$(grep -c "Pending" project-state-management/operations/tasks.md || echo "0")
    echo "   Pending tasks: $PENDING_TASKS"

    # Check for blockers
    if grep -q "BLOCKER" project-state-management/operations/tasks.md; then
        echo "   ⚠️ BLOCKERS FOUND:"
        grep "BLOCKER" project-state-management/operations/tasks.md | head -3
    fi
fi

# 4. Check last update time
echo ""
echo "4. System status..."
if [ -f "project-state-management/core/state.md" ]; then
    LAST_UPDATE=$(grep "last_updated:" project-state-management/core/state.md | cut -d' ' -f2)
    echo "   Last updated: $LAST_UPDATE"

    CURRENT_PHASE=$(grep -A1 "## CURRENT PHASE" project-state-management/core/state.md | tail -1 | sed 's/**//g')
    echo "   Current phase: $CURRENT_PHASE"
fi

# 5. Check for errors
echo ""
echo "5. Error check..."
if [ -f "project-state-management/operations/errors.md" ]; then
    ERROR_COUNT=$(grep -c "## ERROR-" project-state-management/operations/errors.md || echo "0")
    echo "   Total errors logged: $ERROR_COUNT"

    UNRESOLVED=$(grep -c "Status: ⚠️" project-state-management/operations/errors.md || echo "0")
    if [ "$UNRESOLVED" -gt 0 ]; then
        echo "   ⚠️ Unresolved errors: $UNRESOLVED"
    fi
fi

# 6. Display next actions
echo ""
echo "6. Next recommended actions:"
if [ -f "project-state-management/reports/progress.md" ]; then
    grep -A5 "## NEXT STEPS" project-state-management/reports/progress.md | tail -5 | sed 's/^/   /'
fi

echo ""
echo "========================================="
echo "AUTO-MODE READY - SYSTEM TRACKING ACTIVE"
echo "========================================="
echo ""
echo "System will now track:"
echo "• Every 3 conversation iterations"
echo "• All project file updates"
echo "• Claude self-improvement loop"
echo "• Agent performance & evaluation"
echo "• All mistakes & lessons learned"
echo ""
echo "Starting conversation tracking..."
echo ""

# Create initial conversation log entry
CONV_LOG="project-state-management/communications/conversations.md"
if [ -f "$CONV_LOG" ]; then
    echo "---" >> "$CONV_LOG"
    echo "## $(date -u +"%Y-%m-%dT%H:%M:%SZ") - Auto-Mode Startup" >> "$CONV_LOG"
    echo "**Action**: System startup with auto-mode enabled" >> "$CONV_LOG"
    echo "**Status**: ✅ Active" >> "$CONV_LOG"
    echo "**Tracking**: Every 3 iterations, all updates, self-improvement" >> "$CONV_LOG"
    echo "" >> "$CONV_LOG"
fi

# Create startup log
STARTUP_LOG="project-state-management/operations/logs.md"
if [ -f "$STARTUP_LOG" ]; then
    echo "" >> "$STARTUP_LOG"
    echo "---" >> "$STARTUP_LOG"
    echo "## $(date -u +"%Y-%m-%dT%H:%M:%SZ") - Auto-Mode Startup" >> "$STARTUP_LOG"
    echo "**Action**: System started with full auto-mode tracking" >> "$STARTUP_LOG"
    echo "**Features**: " >> "$STARTUP_LOG"
    echo "- Every 3 conversation iterations tracked" >> "$STARTUP_LOG"
    echo "- All project file updates monitored" >> "$STARTUP_LOG"
    echo "- Claude self-improvement loop active" >> "$STARTUP_LOG"
    echo "- Agent performance tracking enabled" >> "$CONV_LOG"
    echo "- All mistakes & lessons recorded" >> "$CONV_LOG"
    echo "**Result**: ✅ System ready for tracking" >> "$STARTUP_LOG"
fi

echo "Startup complete. Ready for work."