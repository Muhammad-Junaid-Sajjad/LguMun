#!/bin/bash
# AUTO-LEARNING HOOK - Runs after every Claude response
# This hook enables real-time learning and state tracking

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Function to update iteration counter
update_iteration_counter() {
    local state_file="$STATE_DIR/core/state.md"
    local current_count=$(grep "iteration_counter:" "$state_file" | awk '{print $2}')
    local next_count=$((current_count + 1))

    # Update iteration counter
    sed -i "s/iteration_counter: $current_count/iteration_counter: $next_count/" "$state_file"

    echo "$next_count"
}

# Function to check if we should report (every 3 iterations)
should_report() {
    local count=$1
    if [ $((count % 3)) -eq 0 ]; then
        return 0  # true
    else
        return 1  # false
    fi
}

# Function to update last_updated timestamp
update_timestamp() {
    local state_file="$STATE_DIR/core/state.md"
    sed -i "s/last_updated: .*/last_updated: $TIMESTAMP/" "$state_file"
}

# Function to log this interaction
log_interaction() {
    local iteration=$1
    echo "## Iteration $iteration - $TIMESTAMP" >> "$STATE_DIR/operations/logs.md"
    echo "**Action**: Auto-learning hook executed" >> "$STATE_DIR/operations/logs.md"
    echo "**Status**: ✅ Tracking active" >> "$STATE_DIR/operations/logs.md"
    echo "" >> "$STATE_DIR/operations/logs.md"
}

# Main execution
main() {
    # Update iteration counter
    ITERATION=$(update_iteration_counter)

    # Update timestamp
    update_timestamp

    # Log this interaction
    log_interaction "$ITERATION"

    # Check if we should generate a report
    if should_report "$ITERATION"; then
        echo "📊 Auto-Mode Report: Iteration $ITERATION reached - generating full state update..."

        # Trigger full state update
        "$PROJECT_ROOT/.claude/scripts/generate-state-report.sh"
    fi
}

# Run main function
main

exit 0
