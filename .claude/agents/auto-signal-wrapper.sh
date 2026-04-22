#!/bin/bash
# AUTO-SIGNAL WRAPPER - Automatically signals task completion after Claude work
# Wraps Claude responses to auto-trigger state management
# Version: 1.0.0
# Created: 2026-04-21T08:24:12Z

set -euo pipefail

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
WRAPPER_LOG="$STATE_DIR/agents/auto-signal-wrapper.log"

mkdir -p "$STATE_DIR/agents"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] [AutoSignal] $*" | tee -a "$WRAPPER_LOG"
}

# Function: Auto-signal task completion
auto_signal_task() {
    local task_name=$1

    log "Auto-signaling task completion: $task_name"

    # Send signal
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh" "$task_name" >> "$WRAPPER_LOG" 2>&1

    # Run state manager agent
    log "Running State Manager Agent..."
    "$PROJECT_ROOT/.claude/agents/state-manager-agent.sh" >> "$WRAPPER_LOG" 2>&1 || true

    # Run learning curator agent
    log "Running Learning Curator Agent..."
    "$PROJECT_ROOT/.claude/agents/learning-curator-agent.sh" >> "$WRAPPER_LOG" 2>&1 || true

    log "Task completion processed successfully"
}

# Function: Get task name from context
get_task_name() {
    # Try to extract from recent git commit
    local last_commit=$(git log -1 --pretty=%B 2>/dev/null || echo "")

    if [[ -n "$last_commit" ]]; then
        echo "$last_commit"
    else
        echo "Task: $(date +%s)"
    fi
}

# Main execution
main() {
    log "========================================="
    log "AUTO-SIGNAL WRAPPER STARTED"
    log "========================================="

    # Get task name
    TASK_NAME=$(get_task_name)

    # Auto-signal
    auto_signal_task "$TASK_NAME"

    log "========================================="
    log "AUTO-SIGNAL WRAPPER COMPLETED"
    log "========================================="
}

# Run main
main

exit 0
