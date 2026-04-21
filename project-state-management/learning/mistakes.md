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

---

## MISTAKE-003: Incorrect Logo File References
**Date**: 2026-04-21T11:50:00Z  
**Files**: `frontend/index.html`, `frontend/committees.html`, `frontend/register.html`, `frontend/success.html`  
**Context**: Using wrong logo file paths and missing LGUMUN logo in footer

### What Happened
- Used `lgumun-logo.jpeg` instead of `lgu-mun-society-logo.jpeg` for LGUMUN Society logo
- Footer had `onerror="this.style.display='none'"` causing LGUMUN logo to not display
- Brand name still showed "LGU MUN" instead of "LGUMUN"

### Root Cause
- Initial logo extraction used wrong filename
- Footer implementation had placeholder logic that hid the logo on error
- Branding wasn't updated to match official "LGUMUN" format

### Impact
- LGUMUN Society logo not visible in footer on all pages
- Inconsistent branding across website
- Missing premium logo styling on footer elements

### Fix Applied
1. Updated all logo references to use `lgu-mun-society-logo.jpeg`
2. Removed `onerror` attributes from footer logos
3. Updated brand names to "LGUMUN 2026" across all pages
4. Added premium glow animations to footer logos
5. Updated navbar logo tooltips to "Home" and "Follow LGUMUN"

### Prevention Strategy
- **Rule**: Always verify logo file paths match actual files in assets folder
- **Checklist**: Before deployment, verify all logo references exist
- **Testing**: Test footer display on all pages to ensure both logos visible
- **Branding Standard**: Use "LGUMUN" (no space) as official format

### Lesson Learned
Logo file names matter - the extracted logo from WhatsApp post has a specific filename that must be used consistently. Also, branding consistency is critical - "LGU MUN" vs "LGUMUN" should be standardized.

### Status
✅ Resolved - All logo references fixed, branding standardized

---

## MISTAKE-004: Confetti Stopping After 10 Seconds
**Date**: 2026-04-21T11:52:00Z  
**File**: `frontend/success.html`  
**Context**: Success page confetti animation stopped after ~10 seconds

### What Happened
The confetti particle system had a frame counter that stopped after 300 frames:
```javascript
if (frame++ > 300) return; // stop after 10s
```

### Root Cause
Confetti loop had artificial stop condition for performance reasons, but this created a poor user experience on the success page where celebration should continue.

### Impact
- Confetti stopped before user could fully celebrate
- Success page felt incomplete
- User experience degraded on key conversion page

### Fix Applied
Removed the frame counter and stop condition:
```javascript
// Removed: if (frame++ > 300) return;
// Confetti now runs forever with requestAnimationFrame loop
```

### Prevention Strategy
- **Rule**: Celebration effects should run indefinitely or until user action
- **Performance**: Use efficient particle rendering to avoid performance issues
- **User Experience**: Success pages should provide full celebration experience

### Lesson Learned
Performance optimizations shouldn't compromise user experience on key pages. Confetti on success page should run as long as needed for full celebration effect.

### Status
✅ Resolved - Confetti now runs forever

---

## MISTAKE-005: LGU Logo Linking to External Site Instead of Home
**Date**: 2026-04-21T11:53:00Z  
**Files**: `frontend/index.html`, `frontend/committees.html`, `frontend/register.html`, `frontend/success.html`  
**Context**: LGU Official logo in navbar linked to admissions.lgu.edu.pk instead of home page

### What Happened
Navbar LGU logo had external link:
```html
<a href="https://admissions.lgu.edu.pk/" target="_blank" ...>
```

### Root Cause
Initial implementation linked to external site for "Visit LGU" functionality, but this broke navigation flow and confused users.

### Impact
- Users lost their place when clicking LGU logo
- Navigation flow broken
- Poor user experience on multi-page journey

### Fix Applied
Changed LGU logo to link to home page:
```html
<a href="/" title="Home" ...>
```

### Prevention Strategy
- **Rule**: Brand/logo links should return to home, not external sites
- **External Links**: Use separate "Visit LGU" button or tooltip for external links
- **Navigation**: Keep users on site for better engagement

### Lesson Learned
Brand logos should always link to home page. External links should be separate, intentional actions (like the LGUMUN Instagram link).

### Status
✅ Resolved - LGU logo now links to home page
