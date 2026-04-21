# MISTAKES DATABASE

## MISTAKE-001: File Write Without Read
**Date**: 2026-04-19T09:45:00Z  
**File**: `specs/001-delegate-registration/spec.md`  
**Context**: Attempting to write to specification file during initialization

### What Happened
Attempted to write to `specs/001-delegate-registration/spec.md` without reading it first.

### Root Cause
Tool requirement: Write tool requires Read tool to be called first on existing files.

### Impact
- 30 second delay
- Minor workflow interruption

### Fix Applied
1. Read file first using Read tool
2. Then write using Write tool
3. Successfully updated file

### Prevention Strategy
- **Rule**: Always use Read tool before Write tool for existing files
- **Checklist**: Add to pre-write validation
- **Automation**: Consider script to enforce this pattern

### Lesson Learned
Tool constraints must be respected. Each tool has specific requirements that must be met before use.

### Status
✅ Resolved and documented

---

## MISTAKE-002: Auto-Mode System Not Actually Tracking
**Date**: 2026-04-21T07:48:44Z  
**File**: `project-state-management/core/state.md`, `operations/logs.md`, `operations/tasks.md`  
**Context**: Auto-mode claimed to be tracking work but files were 18+ hours outdated

### What Happened
The auto-mode system was initialized and claimed to be "FULLY ACTIVATED" with real-time tracking, but it never actually updated any state files during work sessions. Files remained frozen at 2026-04-20T13:11:30Z despite multiple sessions and significant work being done.

### Root Cause
The auto-mode system was **declarative, not functional**. It created configuration files and claimed to track work, but had no actual mechanism to update state files during conversations. The "every 3 iterations" tracking was never implemented.

### Impact
- **High**: Complete loss of project state visibility
- User couldn't see current work status
- Tasks were outdated and irrelevant
- Progress metrics were wrong (95% vs actual 85%)
- Learning system captured nothing from recent sessions
- Audit trail broken for 18+ hours of work

### Fix Applied
1. Manually updated `core/state.md` with current reality
2. Manually updated `operations/tasks.md` with actual pending work
3. Manually added log entry documenting the repair
4. Identified root cause for future prevention

### Prevention Strategy
- **Rule**: Don't claim systems are "active" unless they actually function
- **Verification**: After claiming to activate a system, verify it's actually working
- **Manual Fallback**: Until auto-tracking works, manually update state files after major tasks
- **Honest Assessment**: If a system doesn't work, document it as "planned" not "active"

### Lesson Learned
Declarative systems (config files, documentation) are not the same as functional systems (actual code that runs). Creating a `.claude/auto-startup.sh` script doesn't mean it's being executed. The system needs actual hooks or mechanisms to trigger updates.

### Status
✅ Resolved - State files manually updated, issue documented
