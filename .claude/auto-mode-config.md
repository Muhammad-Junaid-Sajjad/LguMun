# AUTO-MODE SYSTEM CONFIGURATION
# This file configures the fully automated project tracking system
# Last Updated: 2026-04-20T07:41:58Z

## AUTO-MODE FEATURES ENABLED

### 1. Conversation Tracking
- **Enabled**: YES
- **Interval**: Every 3 iterations
- **Track All**: YES (decisions, context, state changes)
- **Storage**: `project-state-management/communications/conversations.md`

### 2. Project File Auto-Updates
- **Enabled**: YES
- **Files Tracked**:
  - `project-state-management/core/state.md`
  - `project-state-management/core/phases.md`
  - `project-state-management/operations/tasks.md`
  - `project-state-management/operations/logs.md`
  - `project-state-management/reports/progress.md`
  - `.specify/memory/constitution.md`
  - `specs/**/*.md`
  - `CLAUDE.md`

### 3. Claude Self-Improvement Loop
- **Enabled**: YES
- **Learn From Mistakes**: YES
- **Extract Lessons**: YES
- **Apply Immediately**: YES
- **Track All Interactions**: YES
- **Storage**: `project-state-management/learning/`

### 4. Agent Performance Tracking
- **Enabled**: YES
- **Results Folder**: `project-state-management/agents/results/`
- **Evaluation Metrics**:
  - Accuracy
  - Completeness
  - Timeliness
  - Quality
- **Auto-Update**: YES
- **Self-Learning**: YES

### 5. Reporting Schedule
- **After Every 3 Iterations**: Full state update
- **Include in Reports**:
  - Current state
  - Tasks completed
  - Progress metrics
  - Errors encountered
  - Mistakes logged
  - Lessons learned
  - Next actions

---

## STARTUP BEHAVIOR

When Claude Code starts in this project:

1. **Auto-Startup Script Runs** (`.claude/auto-startup.sh`)
   - Checks project state
   - Verifies auto-mode status
   - Lists pending tasks
   - Identifies blockers
   - Displays next actions

2. **State Management System Activates**
   - Loads current phase
   - Reads pending tasks
   - Checks for errors
   - Initializes tracking

3. **Conversation Tracking Begins**
   - Every 3 iterations logged
   - All decisions recorded
   - Context preserved
   - State changes tracked

4. **Self-Improvement Loop Starts**
   - Mistakes logged automatically
   - Lessons extracted
   - Improvements applied
   - Next run benefits from learning

---

## ITERATION TRACKING

**Iteration Counter**: Tracks every 3 user prompts

**After Every 3 Iterations**:
1. Update `project-state-management/core/state.md`
2. Update `project-state-management/operations/tasks.md`
3. Update `project-state-management/reports/progress.md`
4. Log conversation in `communications/conversations.md`
5. Record any mistakes in `learning/mistakes.md`
6. Extract lessons in `learning/lessons.md`
7. Report back to user with summary

---

## AGENT TRACKING & EVALUATION

**Agent Results Folder**: `project-state-management/agents/results/`

**Tracked Agents**:
1. Architect Agent
2. Reviewer Agent
3. Validator Agent

**Evaluation Criteria**:
- Accuracy: How correct are the outputs?
- Completeness: Are all requirements met?
- Timeliness: How fast are the results?
- Quality: How production-ready is the work?

**Self-Learning**:
- Agents learn from feedback
- Improvements applied to next run
- Performance metrics tracked
- Results recorded automatically

---

## CLAUDE SELF-IMPROVEMENT PROTOCOL

### Mistake Tracking
- Every error logged with timestamp
- Root cause analysis performed
- Fix applied immediately
- Prevention measures documented

### Lesson Extraction
- After every significant action
- Patterns identified
- Best practices documented
- Applied to future iterations

### Continuous Improvement
- Each mistake becomes a lesson
- Each lesson improves next run
- System gets better over time
- All improvements recorded

---

## FILE UPDATE PROTOCOL

**When Files Are Updated**:
1. After every 3 iterations
2. After every phase completion
3. After every major task completion
4. After every error resolution
5. After every deployment milestone

**What Gets Updated**:
- Phase progress
- Task status
- Completion dates
- Metrics
- Lessons learned
- Next actions

---

## REPORTING FORMAT

**After Every 3 Iterations**:

```
## AUTO-MODE UPDATE REPORT
**Timestamp**: [ISO timestamp]
**Iteration**: [3, 6, 9, etc.]

### State Changes
- [What changed]
- [What changed]

### Tasks Completed
- [Task 1]
- [Task 2]

### Metrics
- Progress: X%
- Phase: [Current phase]
- Status: [Status]

### Lessons Learned
- [Lesson 1]
- [Lesson 2]

### Next Actions
- [Action 1]
- [Action 2]

### Blockers
- [Blocker 1] (if any)
```

---

## ACTIVATION STATUS

**Status**: ✅ FULLY ACTIVATED

**Components Active**:
- ✅ Auto-startup script
- ✅ Conversation tracking
- ✅ Project file auto-updates
- ✅ Claude self-improvement loop
- ✅ Agent performance tracking
- ✅ Real-time state management
- ✅ Automatic reporting

**Next Startup**: System will auto-activate on next Claude Code session

---

## MANUAL TRIGGERS

You can manually trigger updates at any time:
- Type: `@auto-mode update` to force an update
- Type: `@auto-mode report` to get a full report
- Type: `@auto-mode status` to check system status

---

**Configuration File**: `.claude/auto-mode-config.md`  
**Last Updated**: 2026-04-20T07:41:58Z  
**Status**: ACTIVE & READY
