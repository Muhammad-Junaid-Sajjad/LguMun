#!/bin/bash
# STATE MANAGER AGENT - Autonomous Background Agent
# Monitors task completion and updates state files automatically
# Version: 1.0.0
# Created: 2026-04-21T08:05:00Z

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
LOG_FILE="$STATE_DIR/agents/state-manager-agent.log"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Ensure log directory exists
mkdir -p "$STATE_DIR/agents"

# Logging function
log() {
    local level=$1
    shift
    echo "[$TIMESTAMP] [$level] $*" | tee -a "$LOG_FILE"
}

# Error handling
error_handler() {
    local line_no=$1
    log "ERROR" "Script failed at line $line_no"
    log "ERROR" "Last command: $BASH_COMMAND"
    exit 1
}

trap 'error_handler ${LINENO}' ERR

# Start agent
log "INFO" "========================================="
log "INFO" "STATE MANAGER AGENT STARTED"
log "INFO" "========================================="

# Function: Update iteration counter
update_iteration_counter() {
    local state_file="$STATE_DIR/core/state.md"

    if [[ ! -f "$state_file" ]]; then
        log "ERROR" "State file not found: $state_file"
        return 1
    fi

    local current_count=$(grep "iteration_counter:" "$state_file" | awk '{print $2}' || echo "0")
    local next_count=$((current_count + 1))

    sed -i "s/iteration_counter: $current_count/iteration_counter: $next_count/" "$state_file"

    echo "$next_count"
}

# Function: Update timestamp
update_timestamp() {
    local state_file="$STATE_DIR/core/state.md"

    if [[ ! -f "$state_file" ]]; then
        log "ERROR" "State file not found: $state_file"
        return 1
    fi

    sed -i "s/last_updated: .*/last_updated: $TIMESTAMP/" "$state_file"
    log "INFO" "Timestamp updated: $TIMESTAMP"
}

# Function: Log task completion
log_task_completion() {
    local task_name=$1
    local task_result=${2:-"success"}

    local logs_file="$STATE_DIR/operations/logs.md"

    if [[ ! -f "$logs_file" ]]; then
        log "ERROR" "Logs file not found: $logs_file"
        return 1
    fi

    cat >> "$logs_file" << EOF

---
## $TIMESTAMP - Task Completed: $task_name

**Action**: $task_name
**Result**: $task_result
**Logged by**: State Manager Agent (Autonomous)

EOF

    log "INFO" "Task logged: $task_name ($task_result)"
}

# Function: Update progress metrics
update_progress_metrics() {
    local progress_file="$STATE_DIR/reports/progress.md"

    if [[ ! -f "$progress_file" ]]; then
        log "ERROR" "Progress file not found: $progress_file"
        return 1
    fi

    # Count completed tasks
    local completed_count=$(grep -c "^[0-9]*\. ✅" "$STATE_DIR/core/state.md" || echo "0")

    # Update report timestamp
    sed -i "s/\*\*Report Generated\*\*: .*/\*\*Report Generated\*\*: $TIMESTAMP/" "$progress_file"

    log "INFO" "Progress metrics updated: $completed_count tasks completed"
}

# Function: Check if report should be generated (every 3 iterations)
should_generate_report() {
    local iteration=$1
    if [[ $((iteration % 3)) -eq 0 ]]; then
        return 0  # true
    else
        return 1  # false
    fi
}

# Function: Generate full state report
generate_full_report() {
    log "INFO" "Generating full state report..."

    if [[ -x "$PROJECT_ROOT/.claude/scripts/generate-state-report.sh" ]]; then
        "$PROJECT_ROOT/.claude/scripts/generate-state-report.sh" >> "$LOG_FILE" 2>&1
        log "INFO" "Full state report generated successfully"
    else
        log "ERROR" "generate-state-report.sh not found or not executable"
        return 1
    fi
}

# Function: Monitor for task completion events
monitor_task_completion() {
    log "INFO" "Monitoring for task completion events..."

    # Check if there's a task completion signal file
    local signal_file="$STATE_DIR/.task-completed"

    if [[ -f "$signal_file" ]]; then
        local task_name=$(cat "$signal_file")
        log "INFO" "Task completion detected: $task_name"

        # Process the completion
        log_task_completion "$task_name" "success"
        update_timestamp
        update_progress_metrics

        # Remove signal file
        rm -f "$signal_file"

        # Update iteration counter
        local iteration=$(update_iteration_counter)

        # Check if we should generate report
        if should_generate_report "$iteration"; then
            generate_full_report
        fi

        log "INFO" "Task completion processed successfully"
    fi
}

# Function: Health check
health_check() {
    log "INFO" "Running health check..."

    local errors=0

    # Check if state files exist
    local required_files=(
        "$STATE_DIR/core/state.md"
        "$STATE_DIR/operations/logs.md"
        "$STATE_DIR/operations/tasks.md"
        "$STATE_DIR/reports/progress.md"
    )

    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log "ERROR" "Required file missing: $file"
            ((errors++))
        fi
    done

    if [[ $errors -eq 0 ]]; then
        log "INFO" "Health check passed ✅"
        return 0
    else
        log "ERROR" "Health check failed with $errors errors ❌"
        return 1
    fi
}

# Main execution loop
main() {
    log "INFO" "Starting main execution loop..."

    # Run health check
    if ! health_check; then
        log "ERROR" "Health check failed, exiting"
        exit 1
    fi

    # Update timestamp on start
    update_timestamp

    # Monitor for task completion
    monitor_task_completion

    log "INFO" "========================================="
    log "INFO" "STATE MANAGER AGENT COMPLETED"
    log "INFO" "========================================="
}

# Run main function
main

exit 0
