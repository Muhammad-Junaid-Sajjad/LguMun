#!/bin/bash
# LEARNING CURATOR AGENT - Autonomous Background Agent
# Extracts lessons, logs mistakes, applies learnings automatically
# Version: 1.0.0
# Created: 2026-04-21T08:05:00Z

set -euo pipefail  # Exit on error, undefined vars, pipe failures

# Configuration
PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
STATE_DIR="$PROJECT_ROOT/project-state-management"
LOG_FILE="$STATE_DIR/agents/learning-curator-agent.log"
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
log "INFO" "LEARNING CURATOR AGENT STARTED"
log "INFO" "========================================="

# Function: Load all lessons
load_lessons() {
    local lessons_file="$STATE_DIR/learning/lessons.md"

    if [[ ! -f "$lessons_file" ]]; then
        log "ERROR" "Lessons file not found: $lessons_file"
        return 1
    fi

    local lessons_count=$(grep -c "^## LESSON-" "$lessons_file" || echo "0")
    log "INFO" "Loaded $lessons_count lessons"

    echo "$lessons_count"
}

# Function: Load all mistakes
load_mistakes() {
    local mistakes_file="$STATE_DIR/learning/mistakes.md"

    if [[ ! -f "$mistakes_file" ]]; then
        log "ERROR" "Mistakes file not found: $mistakes_file"
        return 1
    fi

    local mistakes_count=$(grep -c "^## MISTAKE-" "$mistakes_file" || echo "0")
    log "INFO" "Loaded $mistakes_count mistakes"

    echo "$mistakes_count"
}

# Function: Check for new mistake signals
check_for_mistakes() {
    log "INFO" "Checking for new mistake signals..."

    local mistake_signal="$STATE_DIR/.mistake-detected"

    if [[ -f "$mistake_signal" ]]; then
        local mistake_data=$(cat "$mistake_signal")
        log "INFO" "New mistake detected: $mistake_data"

        # Process the mistake
        log_new_mistake "$mistake_data"

        # Remove signal file
        rm -f "$mistake_signal"

        log "INFO" "Mistake processed successfully"
    fi
}

# Function: Log new mistake
log_new_mistake() {
    local mistake_data=$1
    local mistakes_file="$STATE_DIR/learning/mistakes.md"

    # Get next mistake number
    local last_mistake=$(grep "^## MISTAKE-" "$mistakes_file" | tail -1 | sed 's/## MISTAKE-\([0-9]*\).*/\1/' || echo "0")
    local next_mistake=$((last_mistake + 1))
    local mistake_id=$(printf "%03d" $next_mistake)

    cat >> "$mistakes_file" << EOF

---

## MISTAKE-$mistake_id: $mistake_data
**Date**: $TIMESTAMP
**Context**: Detected by Learning Curator Agent

### What Happened
$mistake_data

### Root Cause
To be analyzed

### Impact
To be assessed

### Fix Applied
To be documented

### Prevention Strategy
To be defined

### Lesson Learned
To be extracted

### Status
⏳ Under investigation

EOF

    log "INFO" "New mistake logged: MISTAKE-$mistake_id"
}

# Function: Extract lessons from patterns
extract_lessons() {
    log "INFO" "Extracting lessons from patterns..."

    local lesson_signal="$STATE_DIR/.lesson-detected"

    if [[ -f "$lesson_signal" ]]; then
        local lesson_data=$(cat "$lesson_signal")
        log "INFO" "New lesson detected: $lesson_data"

        # Process the lesson
        log_new_lesson "$lesson_data"

        # Remove signal file
        rm -f "$lesson_signal"

        log "INFO" "Lesson processed successfully"
    fi
}

# Function: Log new lesson
log_new_lesson() {
    local lesson_data=$1
    local lessons_file="$STATE_DIR/learning/lessons.md"

    # Get next lesson number
    local last_lesson=$(grep "^## LESSON-" "$lessons_file" | tail -1 | sed 's/## LESSON-\([0-9]*\).*/\1/' || echo "0")
    local next_lesson=$((last_lesson + 1))
    local lesson_id=$(printf "%03d" $next_lesson)

    cat >> "$lessons_file" << EOF

---

## LESSON-$lesson_id: $lesson_data
**Date**: $TIMESTAMP
**Source**: Extracted by Learning Curator Agent

### Context
Pattern detected during work

### Key Insight
$lesson_data

### Best Practice
To be defined

### Application
Apply to all future work

EOF

    log "INFO" "New lesson logged: LESSON-$lesson_id"
}

# Function: Update self-improvement loop metrics
update_metrics() {
    local loop_file="$STATE_DIR/learning/self-improvement-loop.md"

    if [[ ! -f "$loop_file" ]]; then
        log "ERROR" "Self-improvement loop file not found: $loop_file"
        return 1
    fi

    local lessons_count=$(load_lessons)
    local mistakes_count=$(load_mistakes)

    cat >> "$loop_file" << EOF

## Learning Metrics Update - $TIMESTAMP
**Lessons Loaded**: $lessons_count
**Mistakes Reviewed**: $mistakes_count
**Status**: ✅ Active and learning
**Updated by**: Learning Curator Agent (Autonomous)

EOF

    log "INFO" "Self-improvement metrics updated"
}

# Function: Health check
health_check() {
    log "INFO" "Running health check..."

    local errors=0

    # Check if learning files exist
    local required_files=(
        "$STATE_DIR/learning/lessons.md"
        "$STATE_DIR/learning/mistakes.md"
        "$STATE_DIR/learning/self-improvement-loop.md"
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

    # Load current state
    local lessons_count=$(load_lessons)
    local mistakes_count=$(load_mistakes)

    log "INFO" "Current state: $lessons_count lessons, $mistakes_count mistakes"

    # Check for new mistakes
    check_for_mistakes

    # Extract new lessons
    extract_lessons

    # Update metrics
    update_metrics

    log "INFO" "========================================="
    log "INFO" "LEARNING CURATOR AGENT COMPLETED"
    log "INFO" "========================================="
}

# Run main function
main

exit 0
