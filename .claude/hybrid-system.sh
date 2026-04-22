#!/bin/bash
# HYBRID SYSTEM CONTROLLER - Manages automatic/manual state management
# Provides start/stop/status commands for the hybrid system
# Version: 1.0.0
# Created: 2026-04-21T08:24:12Z

set -euo pipefail

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
HYBRID_CONFIG="$STATE_DIR/agents/hybrid-config.conf"
HYBRID_LOG="$STATE_DIR/agents/hybrid-system.log"

mkdir -p "$STATE_DIR/agents"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] [Hybrid] $*" | tee -a "$HYBRID_LOG"
}

# Initialize config
init_config() {
    if [[ ! -f "$HYBRID_CONFIG" ]]; then
        cat > "$HYBRID_CONFIG" << EOF
# Hybrid System Configuration
# Created: $(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Enable/disable automatic state updates
AUTO_STATE_UPDATES=true

# Enable/disable automatic learning
AUTO_LEARNING=true

# Enable/disable automatic health checks
AUTO_HEALTH_CHECK=true

# Log level (DEBUG, INFO, WARN, ERROR)
LOG_LEVEL=INFO

# Status
STATUS=ACTIVE
LAST_UPDATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EOF
        log "Initialized hybrid configuration"
    fi
}

# Start hybrid system
start_hybrid() {
    log "Starting Hybrid System..."

    init_config

    # Enable all features
    sed -i 's/AUTO_STATE_UPDATES=.*/AUTO_STATE_UPDATES=true/' "$HYBRID_CONFIG"
    sed -i 's/AUTO_LEARNING=.*/AUTO_LEARNING=true/' "$HYBRID_CONFIG"
    sed -i 's/AUTO_HEALTH_CHECK=.*/AUTO_HEALTH_CHECK=true/' "$HYBRID_CONFIG"
    sed -i 's/STATUS=.*/STATUS=ACTIVE/' "$HYBRID_CONFIG"
    sed -i "s/LAST_UPDATE=.*/LAST_UPDATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" "$HYBRID_CONFIG"

    log "✅ Hybrid System STARTED"
    log "  - Auto state updates: ENABLED"
    log "  - Auto learning: ENABLED"
    log "  - Auto health checks: ENABLED"
}

# Stop hybrid system
stop_hybrid() {
    log "Stopping Hybrid System..."

    init_config

    # Disable all features
    sed -i 's/AUTO_STATE_UPDATES=.*/AUTO_STATE_UPDATES=false/' "$HYBRID_CONFIG"
    sed -i 's/AUTO_LEARNING=.*/AUTO_LEARNING=false/' "$HYBRID_CONFIG"
    sed -i 's/AUTO_HEALTH_CHECK=.*/AUTO_HEALTH_CHECK=false/' "$HYBRID_CONFIG"
    sed -i 's/STATUS=.*/STATUS=INACTIVE/' "$HYBRID_CONFIG"
    sed -i "s/LAST_UPDATE=.*/LAST_UPDATE=$(date -u +"%Y-%m-%dT%H:%M:%SZ")/" "$HYBRID_CONFIG"

    log "✅ Hybrid System STOPPED"
    log "  - All automatic features disabled"
}

# Get hybrid system status
status_hybrid() {
    init_config

    echo ""
    echo "========================================="
    echo "HYBRID SYSTEM STATUS"
    echo "========================================="
    echo ""

    if grep -q "STATUS=ACTIVE" "$HYBRID_CONFIG"; then
        echo "Status: ✅ ACTIVE"
    else
        echo "Status: ⏸️ INACTIVE"
    fi

    echo ""
    echo "Features:"
    grep "AUTO_" "$HYBRID_CONFIG" | while read line; do
        if [[ $line == *"=true"* ]]; then
            echo "  ✅ $(echo $line | cut -d'=' -f1): ENABLED"
        else
            echo "  ⏸️ $(echo $line | cut -d'=' -f1): DISABLED"
        fi
    done

    echo ""
    echo "Last Update: $(grep 'LAST_UPDATE=' "$HYBRID_CONFIG" | cut -d'=' -f2)"
    echo ""
    echo "========================================="
    echo ""
}

# Manual signal task
signal_task() {
    local task_name=$1

    log "Manual signal: $task_name"

    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh" "$task_name"
    "$PROJECT_ROOT/.claude/agents/state-manager-agent.sh" >> "$HYBRID_LOG" 2>&1 || true
    "$PROJECT_ROOT/.claude/agents/learning-curator-agent.sh" >> "$HYBRID_LOG" 2>&1 || true

    log "Task signaled successfully"
}

# Main
case "${1:-status}" in
    start)
        start_hybrid
        ;;
    stop)
        stop_hybrid
        ;;
    status)
        status_hybrid
        ;;
    signal)
        if [[ -z "${2:-}" ]]; then
            echo "Usage: $0 signal \"Task Name\""
            exit 1
        fi
        signal_task "$2"
        ;;
    *)
        echo "Usage: $0 {start|stop|status|signal \"Task Name\"}"
        exit 1
        ;;
esac

exit 0
