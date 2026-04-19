# ANTI-PATTERNS

## ANTI-PATTERN-001: Scattered State Management
**Pattern**: Project information spread across multiple locations without structure

### Symptoms
- Hard to find current project state
- Decisions documented in multiple places
- Tasks tracked in different systems
- No single source of truth

### Prevention
- Use `/project-state-management/` as central hub
- All state files in one location
- Clear file naming conventions
- YAML frontmatter for metadata

---

## ANTI-PATTERN-002: Ignoring Tool Requirements
**Pattern**: Using tools without meeting their requirements

### Symptoms
- File write errors (e.g., "File has not been read yet")
- Tool failures due to missing prerequisites
- Unnecessary delays from errors

### Prevention
- Always Read before Write for existing files
- Check tool documentation before use
- Build validation into workflow

---

## ANTI-PATTERN-003: No Approval Workflow
**Pattern**: Decisions made without clear approval tracking

### Symptoms
- Unclear who approved what and when
- Re-discussing same topics
- No audit trail for decisions

### Prevention
- Use approvals folder with state transitions
- YAML frontmatter for approval metadata
- Move files between folders on state change

---

## ANTI-PATTERN-004: No Learning from Mistakes
**Pattern**: Errors occur but no mechanism to prevent regression

### Symptoms
- Same mistakes happen repeatedly
- No documentation of what went wrong
- No improvement over time

### Prevention
- Log all errors in errors.md
- Extract lessons in lessons.md
- Update anti-patterns.md regularly
- Apply learning to future actions

---

## ANTI-PATTERN-005: Over-Engineering Early
**Pattern**: Adding complexity before requirements are clear

### Symptoms
- Unnecessary abstractions
- Complex architecture for simple problems
- Delayed delivery due to over-design

### Prevention
- Start with flat structure (as per constitution)
- Add complexity only when needed
- Follow YAGNI principle

---

## ANTI-PATTERN-006: No State Transitions
**Pattern**: Files stuck in initial state without tracking progress

### Symptoms
- Pending items never move to approved
- No visibility into what's been executed
- No audit trail for completed work

### Prevention
- Use subfolders for each state (pending, approved, executed, history)
- Update YAML frontmatter on state change
- Move files between folders automatically

---

## ANTI-PATTERN-007: No Continuous Improvement
**Pattern**: System doesn't learn from its own actions

### Symptoms
- Same errors repeat
- No pattern recognition
- Stagnant quality

### Prevention
- Log all actions and outcomes
- Extract lessons from patterns
- Update learning files automatically
- Apply learning to future actions

---

## ANTI-PATTERN-008: Deep Agent Hierarchies
**Pattern**: Creating sub-sub-specialist agents (too deep)

### Symptoms
- Complex agent configuration
- Hard to maintain
- Over-engineered architecture

### Prevention
- Max 2-level depth (agent → subagent)
- Keep subagents focused on specific tasks
- Avoid unnecessary nesting

---

## ANTI-PATTERN-009: Static State Files
**Pattern**: State files created but never updated

### Symptoms
- State doesn't reflect current reality
- Tasks marked complete but not executed
- No progress tracking

### Prevention
- Update state.md after every meaningful action
- Update tasks.md on task completion
- Update logs.md chronologically
- Update progress.md regularly

---

## ANTI-PATTERN-010: No Change Tracking
**Pattern**: File changes not documented

### Symptoms
- Hard to know what changed and when
- No audit trail
- Difficult to rollback

### Prevention
- Use CHANGELOG.md for all notable changes
- Document format and version
- Include status and notes for each change
