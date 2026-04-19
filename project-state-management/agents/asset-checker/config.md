# ASSET-CHECKER AGENT

**Agent Type**: Subagent (Asset Management Specialist)  
**Purpose**: Verify all frontend assets exist and are correct  
**Status**: Active  
**Created**: 2026-04-19T12:32:00Z

---

## RESPONSIBILITIES

1. **Logo Verification**
   - Verify logo file exists
   - Verify logo format (PNG)
   - Verify logo dimensions
   - Verify logo referenced correctly in HTML

2. **Photo Verification**
   - Verify all 3 photos exist
   - Verify photo format (JPEG)
   - Verify photo dimensions
   - Verify photos referenced correctly in HTML

3. **CSS File Verification**
   - Verify all CSS files exist
   - Verify CSS files linked in HTML
   - Verify no broken CSS imports
   - Verify Google Fonts loaded

4. **JavaScript File Verification**
   - Verify all JS files exist
   - Verify JS files linked in HTML
   - Verify no broken JS imports
   - Verify no syntax errors in JS

---

## ACTIVATION

**Trigger**: After Phase D (Frontend) asset additions  
**Auto-run**: Yes - runs after asset changes  
**Manual invoke**: `/asset-checker`

---

## ASSET CHECKLIST

### Check 1: Logo File
```bash
# Verify logo exists
ls -la frontend/assets/logo/lgumun-logo.png

# Expected: File exists, readable
# -rw-rw-r-- 1 user user XXXX Apr 19 12:00 frontend/assets/logo/lgumun-logo.png
```

### Check 2: Photo Files
```bash
# Verify all photos exist
ls -la frontend/assets/photos/photo*.jpg

# Expected: 3 files
# photo1.jpg
# photo2.jpg
# photo3.jpg
```

### Check 3: CSS Files
```bash
# Verify CSS files exist
ls -la frontend/css/

# Expected:
# theme.css
# main.css
# responsive.css
```

### Check 4: JavaScript Files
```bash
# Verify JS files exist
ls -la frontend/js/

# Expected:
# api.js
# register.js
# success.js
# committees.js
```

### Check 5: HTML References
```bash
# Check logo referenced in HTML
grep -r "lgumun-logo.png" frontend/ --include="*.html"

# Expected: 4 matches (one per page)
```

### Check 6: CSS Imports
```bash
# Check CSS linked in HTML
grep -r "css/theme.css\|css/main.css\|css/responsive.css" frontend/ --include="*.html"

# Expected: All CSS files linked on all pages
```

### Check 7: JS Imports
```bash
# Check JS linked in HTML
grep -r "js/api.js\|js/register.js\|js/success.js\|js/committees.js" frontend/ --include="*.html"

# Expected: Correct JS files on each page
```

---

## ASSET REPORT FORMAT

```
ASSET VERIFICATION REPORT
==========================
Timestamp: 2026-04-19T12:00:00Z

Check 1: Logo
├─ File: frontend/assets/logo/lgumun-logo.png
├─ Status: ✅ EXISTS
├─ Format: PNG ✅
├─ Size: 48KB
└─ Referenced: 4 pages ✅

Check 2: Photos
├─ photo1.jpg: ✅ EXISTS (220KB)
├─ photo2.jpg: ✅ EXISTS (215KB)
├─ photo3.jpg: ✅ EXISTS (218KB)
└─ All referenced: ✅

Check 3: CSS Files
├─ theme.css: ✅ EXISTS (2.1KB)
├─ main.css: ✅ EXISTS (8.5KB)
├─ responsive.css: ✅ EXISTS (1.2KB)
└─ All linked: ✅

Check 4: JavaScript Files
├─ api.js: ✅ EXISTS (1.2KB)
├─ register.js: ✅ EXISTS (3.4KB)
├─ success.js: ✅ EXISTS (0.8KB)
├─ committees.js: ✅ EXISTS (2.1KB)
└─ All linked: ✅

Check 5: HTML Pages
├─ index.html: ✅ EXISTS
├─ register.html: ✅ EXISTS
├─ success.html: ✅ EXISTS
└─ committees.html: ✅ EXISTS

Check 6: Broken Links
├─ CSS imports: ✅ All valid
├─ JS imports: ✅ All valid
├─ Image paths: ✅ All valid
└─ Broken links: 0

OVERALL STATUS: ✅ ALL ASSETS VERIFIED
```

---

## FAILURE EXAMPLE

```
ASSET VERIFICATION REPORT
==========================
Timestamp: 2026-04-19T12:00:00Z

Check 1: Logo
├─ File: frontend/assets/logo/lgumun-logo.png
├─ Status: ❌ MISSING
└─ Action: Copy logo file to frontend/assets/logo/

Check 2: Photos
├─ photo1.jpg: ✅ EXISTS
├─ photo2.jpg: ❌ MISSING
├─ photo3.jpg: ✅ EXISTS
└─ Action: Copy photo2.jpg to frontend/assets/photos/

OVERALL STATUS: ❌ MISSING ASSETS
Action: ADD MISSING FILES BEFORE DEPLOYMENT
```

---

## WORKFLOW

```
┌─────────────────────────────────────────────────────────────┐
│                ASSET-CHECKER WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Detect asset folder changes                             │
│  2. Check logo file exists                                  │
│  3. Check all 3 photos exist                                │
│  4. Check all CSS files exist                               │
│  5. Check all JS files exist                                │
│  6. Verify HTML references                                  │
│  7. Check for broken links                                  │
│  8. Generate asset report                                   │
│  9. If missing: WARN user + list missing files              │
│  10. If all present: PASS                                   │
│  11. Log to agent-logs.md                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## SUCCESS CRITERIA

- Logo file exists and is PNG
- All 3 photos exist and are JPEG
- All CSS files exist and linked
- All JS files exist and linked
- No broken links
- All HTML pages present

---

## LEARNING FROM ACTIONS

Each asset-checker action contributes to:
- `learning/lessons.md` - Asset management best practices
- `learning/anti-patterns.md` - Common asset issues
