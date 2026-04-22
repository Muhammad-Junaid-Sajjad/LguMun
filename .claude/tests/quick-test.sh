#!/bin/bash
# QUICK STRESS TEST - Fast validation of agent functionality
# Version: 1.0.0

PROJECT_ROOT="/home/nauman_sajjad/Desktop/LGU/Lgu-Mun"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "========================================="
echo "QUICK STRESS TEST - $TIMESTAMP"
echo "========================================="
echo ""

PASSED=0
FAILED=0

# Test 1: State Manager Agent
echo "TEST 1: State Manager Agent Basic Run"
if ./.claude/agents/state-manager-agent.sh > /dev/null 2>&1; then
    echo "✅ PASSED"
    ((PASSED++))
else
    echo "❌ FAILED"
    ((FAILED++))
fi

# Test 2: Learning Curator Agent
echo "TEST 2: Learning Curator Agent Basic Run"
if ./.claude/agents/learning-curator-agent.sh > /dev/null 2>&1; then
    echo "✅ PASSED"
    ((PASSED++))
else
    echo "❌ FAILED"
    ((FAILED++))
fi

# Test 3: Task Completion Signal
echo "TEST 3: Task Completion Signal"
if ./.claude/agents/signal-task-completion.sh "Quick Test Task" > /dev/null 2>&1; then
    echo "✅ PASSED"
    ((PASSED++))
else
    echo "❌ FAILED"
    ((FAILED++))
fi

# Test 4: Full Workflow
echo "TEST 4: Full Workflow (Signal → State Manager → Learning Curator)"
if ./.claude/agents/signal-task-completion.sh "Workflow Test" > /dev/null 2>&1 && \
   ./.claude/agents/state-manager-agent.sh > /dev/null 2>&1 && \
   ./.claude/agents/learning-curator-agent.sh > /dev/null 2>&1; then
    echo "✅ PASSED"
    ((PASSED++))
else
    echo "❌ FAILED"
    ((FAILED++))
fi

# Test 5: Concurrent Signals (5 rapid signals)
echo "TEST 5: Concurrent Signals (5 rapid)"
SUCCESS=true
for i in {1..5}; do
    if ! ./.claude/agents/signal-task-completion.sh "Concurrent Test $i" > /dev/null 2>&1; then
        SUCCESS=false
        break
    fi
done
if $SUCCESS; then
    echo "✅ PASSED"
    ((PASSED++))
else
    echo "❌ FAILED"
    ((FAILED++))
fi

# Test 6: State File Updates
echo "TEST 6: State File Timestamp Updates"
BEFORE=$(grep 'last_updated:' project-state-management/core/state.md | awk '{print $2}')
sleep 1
./.claude/agents/state-manager-agent.sh > /dev/null 2>&1
AFTER=$(grep 'last_updated:' project-state-management/core/state.md | awk '{print $2}')
if [ "$AFTER" != "$BEFORE" ]; then
    echo "✅ PASSED (Updated: $BEFORE → $AFTER)"
    ((PASSED++))
else
    echo "❌ FAILED (No update)"
    ((FAILED++))
fi

# Test 7: Agent Orchestrator
echo "TEST 7: Agent Orchestrator"
if [ -x ./.claude/agents/agent-orchestrator.sh ]; then
    if ./.claude/agents/agent-orchestrator.sh > /dev/null 2>&1; then
        echo "✅ PASSED"
        ((PASSED++))
    else
        echo "❌ FAILED"
        ((FAILED++))
    fi
else
    echo "⚠️ SKIPPED (orchestrator not executable)"
fi

echo ""
echo "========================================="
echo "RESULTS:"
echo "  Passed: $PASSED"
echo "  Failed: $FAILED"
echo "  Success Rate: $(awk "BEGIN {printf \"%.1f\", ($PASSED/($PASSED+$FAILED))*100}")%"
echo "========================================="

if [ $FAILED -eq 0 ]; then
    echo "✅ ALL TESTS PASSED"
    exit 0
else
    echo "❌ SOME TESTS FAILED"
    exit 1
fi
