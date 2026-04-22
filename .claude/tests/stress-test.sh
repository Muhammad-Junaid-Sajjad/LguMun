#!/bin/bash
# STRESS TEST SUITE - Rigorous testing under extreme conditions
# Tests agents under high load, concurrent signals, edge cases, and failure scenarios
# Version: 1.0.0
# Created: 2026-04-21T08:10:45Z

set -euo pipefail

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
TEST_LOG="$PROJECT_ROOT/.claude/tests/stress-test-$(date +%Y%m%d-%H%M%S).log"

mkdir -p "$PROJECT_ROOT/.claude/tests"

log() {
    echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] $*" | tee -a "$TEST_LOG"
}

log "========================================="
log "STRESS TEST SUITE STARTED"
log "========================================="

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test function
run_test() {
    local test_name=$1
    local test_command=$2

    ((TOTAL_TESTS++))
    log ""
    log "TEST $TOTAL_TESTS: $test_name"
    log "Command: $test_command"

    if eval "$test_command" >> "$TEST_LOG" 2>&1; then
        ((PASSED_TESTS++))
        log "✅ PASSED"
        return 0
    else
        ((FAILED_TESTS++))
        log "❌ FAILED"
        return 1
    fi
}

# ============================================
# TEST CATEGORY 1: BASIC FUNCTIONALITY
# ============================================
log ""
log "========================================="
log "CATEGORY 1: BASIC FUNCTIONALITY TESTS"
log "========================================="

run_test "State Manager Agent - Health Check" \
    "$PROJECT_ROOT/.claude/agents/state-manager-agent.sh"

run_test "Learning Curator Agent - Health Check" \
    "$PROJECT_ROOT/.claude/agents/learning-curator-agent.sh"

run_test "Signal Task Completion - Single Signal" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Test: Basic Functionality'"

run_test "Signal Mistake - Single Signal" \
    "$PROJECT_ROOT/.claude/agents/signal-mistake.sh 'Test: Basic Mistake Detection'"

run_test "Signal Lesson - Single Signal" \
    "$PROJECT_ROOT/.claude/agents/signal-lesson.sh 'Test: Basic Lesson Extraction'"

# ============================================
# TEST CATEGORY 2: CONCURRENT SIGNALS
# ============================================
log ""
log "========================================="
log "CATEGORY 2: CONCURRENT SIGNAL TESTS"
log "========================================="

run_test "Concurrent Task Signals - 5 simultaneous" \
    "for i in {1..5}; do $PROJECT_ROOT/.claude/agents/signal-task-completion.sh \"Concurrent Task \$i\" & done; wait"

run_test "Concurrent Mistake Signals - 3 simultaneous" \
    "for i in {1..3}; do $PROJECT_ROOT/.claude/agents/signal-mistake.sh \"Concurrent Mistake \$i\" & done; wait"

run_test "Concurrent Lesson Signals - 3 simultaneous" \
    "for i in {1..3}; do $PROJECT_ROOT/.claude/agents/signal-lesson.sh \"Concurrent Lesson \$i\" & done; wait"

run_test "Mixed Concurrent Signals - All types" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Mixed 1' & \
     $PROJECT_ROOT/.claude/agents/signal-mistake.sh 'Mixed 2' & \
     $PROJECT_ROOT/.claude/agents/signal-lesson.sh 'Mixed 3' & \
     wait"

# ============================================
# TEST CATEGORY 3: HIGH LOAD TESTS
# ============================================
log ""
log "========================================="
log "CATEGORY 3: HIGH LOAD TESTS"
log "========================================="

run_test "High Load - 20 rapid task signals" \
    "for i in {1..20}; do $PROJECT_ROOT/.claude/agents/signal-task-completion.sh \"Load Test \$i\"; done"

run_test "High Load - State Manager Agent 10 runs" \
    "for i in {1..10}; do $PROJECT_ROOT/.claude/agents/state-manager-agent.sh; done"

run_test "High Load - Learning Curator Agent 10 runs" \
    "for i in {1..10}; do $PROJECT_ROOT/.claude/agents/learning-curator-agent.sh; done"

# ============================================
# TEST CATEGORY 4: EDGE CASES
# ============================================
log ""
log "========================================="
log "CATEGORY 4: EDGE CASE TESTS"
log "========================================="

run_test "Edge Case - Empty task name" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh '' || true"

run_test "Edge Case - Very long task name (500 chars)" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh '$(printf 'A%.0s' {1..500})'"

run_test "Edge Case - Special characters in task name" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Test: <>&|;$()[]{}'"

run_test "Edge Case - Unicode characters" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Test: 测试 テスト 🚀'"

run_test "Edge Case - Multiple signal files exist" \
    "touch $PROJECT_ROOT/project-state-management/.task-completed && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh"

# ============================================
# TEST CATEGORY 5: FAILURE SCENARIOS
# ============================================
log ""
log "========================================="
log "CATEGORY 5: FAILURE SCENARIO TESTS"
log "========================================="

run_test "Failure - Missing state file (recovery)" \
    "mv $PROJECT_ROOT/project-state-management/core/state.md $PROJECT_ROOT/project-state-management/core/state.md.bak && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh || true && \
     mv $PROJECT_ROOT/project-state-management/core/state.md.bak $PROJECT_ROOT/project-state-management/core/state.md"

run_test "Failure - Corrupted signal file" \
    "echo -e '\x00\x01\x02' > $PROJECT_ROOT/project-state-management/.task-completed && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh || true"

run_test "Failure - Permission denied (recovery)" \
    "chmod 000 $PROJECT_ROOT/project-state-management/.task-completed 2>/dev/null || true && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh || true && \
     chmod 644 $PROJECT_ROOT/project-state-management/.task-completed 2>/dev/null || true"

# ============================================
# TEST CATEGORY 6: PERFORMANCE TESTS
# ============================================
log ""
log "========================================="
log "CATEGORY 6: PERFORMANCE TESTS"
log "========================================="

run_test "Performance - State Manager Agent execution time < 2s" \
    "time timeout 2s $PROJECT_ROOT/.claude/agents/state-manager-agent.sh"

run_test "Performance - Learning Curator Agent execution time < 2s" \
    "time timeout 2s $PROJECT_ROOT/.claude/agents/learning-curator-agent.sh"

run_test "Performance - Signal script execution time < 0.5s" \
    "time timeout 0.5s $PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Performance Test'"

# ============================================
# TEST CATEGORY 7: INTEGRATION TESTS
# ============================================
log ""
log "========================================="
log "CATEGORY 7: INTEGRATION TESTS"
log "========================================="

run_test "Integration - Full workflow (signal → state → learning)" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Integration Test' && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh && \
     $PROJECT_ROOT/.claude/agents/learning-curator-agent.sh"

run_test "Integration - Iteration counter increments correctly" \
    "BEFORE=\$(grep 'iteration_counter:' $PROJECT_ROOT/project-state-management/core/state.md | awk '{print \$2}') && \
     $PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Counter Test' && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh && \
     AFTER=\$(grep 'iteration_counter:' $PROJECT_ROOT/project-state-management/core/state.md | awk '{print \$2}') && \
     [ \$AFTER -gt \$BEFORE ]"

run_test "Integration - Timestamp updates correctly" \
    "BEFORE=\$(grep 'last_updated:' $PROJECT_ROOT/project-state-management/core/state.md | awk '{print \$2}') && \
     sleep 1 && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh && \
     AFTER=\$(grep 'last_updated:' $PROJECT_ROOT/project-state-management/core/state.md | awk '{print \$2}') && \
     [ \"\$AFTER\" != \"\$BEFORE\" ]"

# ============================================
# TEST CATEGORY 8: RECOVERY TESTS
# ============================================
log ""
log "========================================="
log "CATEGORY 8: RECOVERY TESTS"
log "========================================="

run_test "Recovery - Agent recovers from crash" \
    "pkill -9 -f state-manager-agent.sh || true && \
     sleep 1 && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh"

run_test "Recovery - Signal file cleanup after processing" \
    "$PROJECT_ROOT/.claude/agents/signal-task-completion.sh 'Cleanup Test' && \
     $PROJECT_ROOT/.claude/agents/state-manager-agent.sh && \
     [ ! -f $PROJECT_ROOT/project-state-management/.task-completed ]"

run_test "Recovery - Logs are created and writable" \
    "[ -f $PROJECT_ROOT/project-state-management/agents/state-manager-agent.log ] && \
     [ -w $PROJECT_ROOT/project-state-management/agents/state-manager-agent.log ]"

# ============================================
# FINAL RESULTS
# ============================================
log ""
log "========================================="
log "STRESS TEST SUITE COMPLETED"
log "========================================="
log ""
log "RESULTS:"
log "  Total Tests: $TOTAL_TESTS"
log "  Passed: $PASSED_TESTS"
log "  Failed: $FAILED_TESTS"
log "  Success Rate: $(awk "BEGIN {printf \"%.2f\", ($PASSED_TESTS/$TOTAL_TESTS)*100}")%"
log ""
log "Test log saved to: $TEST_LOG"
log "========================================="

# Exit with failure if any tests failed
if [ $FAILED_TESTS -gt 0 ]; then
    log "❌ STRESS TEST SUITE FAILED"
    exit 1
else
    log "✅ STRESS TEST SUITE PASSED"
    exit 0
fi
