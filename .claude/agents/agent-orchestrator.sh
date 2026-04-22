#!/bin/bash
# AGENT ORCHESTRATOR - Central management system for all agents
# Coordinates agent execution, handles priorities, and manages resources
# Version: 1.0.0

set -euo pipefail

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
ORCHESTRATOR_LOG="$STATE_DIR/agents/orchestrator.log"

mkdir -p "$STATE_DIR/agents"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] [Orchestrator] $*" | tee -a "$ORCHESTRATOR_LOG"
}

log "========================================="
log "AGENT ORCHESTRATOR STARTED"
log "========================================="

# Execute state manager agent
if [[ -x "$PROJECT_ROOT/.claude/agents/state-manager-agent.sh" ]]; then
    log "Executing State Manager Agent..."
    "$PROJECT_ROOT/.claude/agents/state-manager-agent.sh" >> "$ORCHESTRATOR_LOG" 2>&1 || true
fi

# Execute learning curator agent
if [[ -x "$PROJECT_ROOT/.claude/agents/learning-curator-agent.sh" ]]; then
    log "Executing Learning Curator Agent..."
    "$PROJECT_ROOT/.claude/agents/learning-curator-agent.sh" >> "$ORCHESTRATOR_LOG" 2>&1 || true
fi

log "========================================="
log "AGENT ORCHESTRATOR COMPLETED"
log "========================================="

exit 0
