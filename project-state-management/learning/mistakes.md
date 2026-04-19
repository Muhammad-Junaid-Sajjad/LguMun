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

## MISTAKE-002: None Yet
**Date**: N/A  
**File**: N/A  
**Context**: No additional mistakes identified

### What Happened
N/A

### Root Cause
N/A

### Impact
N/A

### Fix Applied
N/A

### Prevention Strategy
N/A

### Lesson Learned
N/A

### Status
✅ No additional mistakes
