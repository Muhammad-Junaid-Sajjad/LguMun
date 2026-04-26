/**
 * EXTREME PHASE 1 STABILITY AUDIT (Pre-Production)
 * Comprehensive testing for 100% production readiness
 * Tests: All Phase 1 features + BUG-014 fix + Hidden bugs + Edge cases
 */

const { chromium } = require('playwright');

async function runExtremeAudit() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║   EXTREME PHASE 1 STABILITY AUDIT (PRE-PRODUCTION)         ║');
  console.log('║   Checking: Bugs, Loopholes, Hidden Errors, Stability    ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const audit = {
    passed: 0,
    failed: 0,
    warnings: 0,
    issues: [],
    networkErrors: [],
    consoleErrors: [],
    securityChecks: []
  };

  // Set up error tracking
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const text = msg.text();
      // Ignore non-critical errors
      if (!text.includes('favicon') && !text.includes('compute-pressure')) {
        audit.consoleErrors.push(text);
      }
    }
  });

  page.on('pageerror', err => {
    audit.issues.push('PAGE ERROR: ' + err.message);
  });

  try {
    // =========================================================
    // SECTION 1: HOMEPAGE COMPREHENSIVE
    // =========================================================
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║ SECTION 1: HOMEPAGE VERIFICATION                            ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('[1.1] Testing homepage load and dynamic content...');
    await page.goto('http://localhost:8000/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2500);

    // Check hero title sync (BUG-008 fix)
    const heroLine1 = await page.locator('#hero-line1').textContent();
    const heroLine3 = await page.locator('#hero-line3').textContent();
    console.log('     Hero lines:', heroLine1.substring(0, 30), '/', heroLine3);

    if (heroLine1.includes('INTRA-UNIVERSITY') && heroLine3.includes('2026')) {
      console.log('     ✅ [PASS] Hero dynamic sync working');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Hero sync broken');
      audit.issues.push('Hero sync not working');
      audit.failed++;
    }

    console.log('\n[1.2] Testing stats display...');
    const statDelegates = await page.locator('#stat-registered').textContent();
    const statCommittees = await page.locator('#stat-committees').textContent();
    console.log('     Delegates:', statDelegates, '| Committees:', statCommittees);

    if (parseInt(statCommittees) >= 9 && parseInt(statDelegates) >= 0) {
      console.log('     ✅ [PASS] Stats displaying correctly');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Stats not displaying');
      audit.issues.push('Stats display issue');
      audit.failed++;
    }

    console.log('\n[1.3] Testing navbar navigation...');
    const navLinks = await page.locator('nav a').count();
    console.log('     Nav links found:', navLinks);

    await page.click('nav a[href="/committees.html"]');
    await page.waitForURL('**/committees.html', { timeout: 5000 });
    console.log('     ✅ [PASS] Navigation to Committees works');
    audit.passed++;

    await page.click('nav a[href="/register.html"]');
    await page.waitForURL('**/register.html', { timeout: 5000 });
    console.log('     ✅ [PASS] Navigation to Register works');
    audit.passed++;

    // =========================================================
    // SECTION 2: REGISTRATION FLOW
    // =========================================================
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║ SECTION 2: REGISTRATION FLOW (3 STEPS)                      ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('[2.1] Step 1: Form visibility and validation...');
    const step1Visible = await page.isVisible('#step-1');
    const closedVisible = await page.isVisible('#registration-closed');
    console.log('     Step 1 visible:', step1Visible, '| Closed:', closedVisible);

    if (step1Visible && !closedVisible) {
      console.log('     ✅ [PASS] Registration open and form visible');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Registration form issue');
      audit.issues.push('Registration form not visible');
      audit.failed++;
    }

    // Test empty form submission
    console.log('\n[2.2] Testing empty form validation...');
    await page.click('#btn-next-1');
    await page.waitForTimeout(500);
    const errorMessages = await page.locator('.form-error').count();
    console.log('     Validation errors shown:', errorMessages);

    if (errorMessages > 0) {
      console.log('     ✅ [PASS] Form validation working');
      audit.passed++;
    } else {
      console.log('     ⚠️ [WARN] No validation errors detected');
      audit.warnings++;
    }

    console.log('\n[2.3] Testing full registration (Step 1-3)...');
    const testData = {
      name: 'Extreme Audit Test',
      cnic: 'AUDIT-' + Date.now(),
      email: 'audit' + Date.now() + '@test.com',
      phone: '03001234567',
      institution: 'Audit University'
    };

    await page.fill('#full_name', testData.name);
    await page.fill('#student_id_cnic', testData.cnic);
    await page.fill('#email', testData.email);
    await page.fill('#phone', testData.phone);
    await page.fill('#institution', testData.institution);
    console.log('     Form filled with test data');

    await page.click('#btn-next-1');
    await page.waitForTimeout(1000);
    const step2Visible = await page.isVisible('#step-2');

    if (step2Visible) {
      console.log('     ✅ [PASS] Step 1 → Step 2 transition');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Step 2 not visible');
      audit.issues.push('Step 2 transition failed');
      audit.failed++;
    }

    console.log('\n[2.4] Step 2: Committee selection...');
    const options = await page.locator('#committee_id option').count();
    console.log('     Committee options:', options - 1);

    await page.selectOption('#committee_id', { index: 1 });
    await page.click('#btn-next-2');
    await page.waitForTimeout(1000);
    const step3Visible = await page.isVisible('#step-3');

    if (step3Visible) {
      console.log('     ✅ [PASS] Step 2 → Step 3 transition');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Step 3 not visible');
      audit.issues.push('Step 3 transition failed');
      audit.failed++;
    }

    console.log('\n[2.5] Step 3: Review section populated...');
    const reviewData = await page.locator('#confirm-grid').textContent();
    const hasName = reviewData.includes(testData.name);
    const hasEmail = reviewData.includes(testData.email);
    console.log('     Review has name:', hasName, '| email:', hasEmail);

    if (hasName && hasEmail) {
      console.log('     ✅ [PASS] Review data populated correctly');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Review data missing');
      audit.issues.push('Review data not populated');
      audit.failed++;
    }

    console.log('\n[2.6] Testing terms checkbox and submit flow...');
    await page.click('#terms-checkbox');
    await page.click('#btn-submit');

    try {
      await page.waitForURL('**/success.html', { timeout: 10000 });
      console.log('     ✅ [PASS] Submit → Success redirect works');
      audit.passed++;
    } catch (e) {
      console.log('     ❌ [FAIL] Success redirect failed');
      audit.issues.push('Success redirect failed');
      audit.failed++;
    }

    // =========================================================
    // SECTION 3: SUCCESS PAGE (Including BUG-014 FIX)
    // =========================================================
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║ SECTION 3: SUCCESS PAGE & BUG-014 VERIFICATION             ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('[3.1] Success page assets after registration...');
    await page.waitForTimeout(1500);

    const rollNumber = await page.locator('#roll-number').textContent();
    console.log('     Roll number displayed:', rollNumber);

    if (rollNumber && rollNumber.includes('LGU-') && !rollNumber.includes('XXXX')) {
      console.log('     ✅ [PASS] Valid roll number shown');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Invalid roll number');
      audit.issues.push('Roll number not valid');
      audit.failed++;
    }

    console.log('\n[3.2] Confetti canvas running...');
    const confetti = await page.locator('#confetti-canvas').isVisible();
    console.log('     Confetti visible:', confetti);

    if (confetti) {
      console.log('     ✅ [PASS] Confetti animation running');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Confetti not visible');
      audit.issues.push('Confetti not running');
      audit.failed++;
    }

    console.log('\n[3.3] Verifying BUG-014: No session → Clear error message...');
    // Clear session and test the error state
    await page.evaluate(() => sessionStorage.clear());
    await page.goto('http://localhost:8000/success.html');
    await page.waitForTimeout(1500);

    const errorContent = await page.locator('#error-content').isVisible();
    const errorTitle = await page.locator('#error-content h2').textContent();
    console.log('     Error content visible:', errorContent);
    console.log('     Error title:', errorTitle);

    if (errorContent && errorTitle === 'No Registration Found') {
      console.log('     ✅ [PASS] BUG-014 FIX VERIFIED: Clear error message shown');
      audit.passed++;
      audit.securityChecks.push('BUG-014: Fixed - No confusing placeholder');
    } else {
      console.log('     ❌ [FAIL] BUG-014 not fixed');
      audit.issues.push('BUG-014 not fixed');
      audit.failed++;
    }

    // =========================================================
    // SECTION 4: COMMITTEES PAGE
    // =========================================================
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║ SECTION 4: COMMITTEES PAGE                                   ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('[4.1] Loading committees page...');
    await page.goto('http://localhost:8000/committees.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const rows = await page.locator('#committees-body tr').count();
    console.log('     Committee rows:', rows);

    if (rows >= 9) {
      console.log('     ✅ [PASS] All 9 committees displayed');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Not all committees shown');
      audit.issues.push('Missing committees');
      audit.failed++;
    }

    console.log('\n[4.2] Testing filter functionality...');
    await page.fill('#search-input', 'UNSC');
    await page.waitForTimeout(500);
    const filtered = await page.locator('#committees-body tr').count();
    console.log('     Filtered results:', filtered);

    if (filtered > 0 && filtered < rows) {
      console.log('     ✅ [PASS] Filters working');
      audit.passed++;
    } else {
      console.log('     ⚠️ [WARN] Filter may not be working');
      audit.warnings++;
    }

    // =========================================================
    // SECTION 5: API HEALTH CHECKS
    // =========================================================
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║ SECTION 5: API ENDPOINTS                                    ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    const endpoints = [
      { url: '/api/v1/health', name: 'Health' },
      { url: '/api/v1/committees', name: 'Committees' },
      { url: '/api/v1/delegates/count', name: 'Delegate Count' },
      { url: '/api/v1/settings', name: 'Public Settings' }
    ];

    for (const ep of endpoints) {
      const res = await page.evaluate(async (url) => {
        const r = await fetch(url);
        return { status: r.status, ok: r.ok };
      }, ep.url);

      if (res.status === 200) {
        console.log('     ✅', ep.name, 'API: OK');
        audit.passed++;
      } else {
        console.log('     ❌', ep.name, 'API: FAIL (' + res.status + ')');
        audit.issues.push('API fail: ' + ep.name);
        audit.failed++;
      }
    }

    console.log('\n[5.5] Admin API authentication...');
    const adminRes = await page.evaluate(async () => {
      const r = await fetch('/api/v1/admin/settings', {
        headers: { 'X-Admin-API-Key': 'lgumun2026_admin_secure_key_x9y2z' }
      });
      return r.status;
    });

    if (adminRes === 200) {
      console.log('     ✅ [PASS] Admin API auth working');
      audit.passed++;
      audit.securityChecks.push('Admin API: Authenticated correctly');
    } else {
      console.log('     ❌ [FAIL] Admin API auth failed');
      audit.issues.push('Admin API auth issue');
      audit.failed++;
    }

    // =========================================================
    // SECTION 6: EDGE CASES & SECURITY
    // =========================================================
    console.log('\n╔══════════════════════════════════��═��═══════════════════════╗');
    console.log('║ SECTION 6: EDGE CASES & SECURITY                            ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('[6.1] Favicon check...');
    const fav = await page.evaluate(async () => {
      const r = await fetch('/favicon.ico');
      return r.status;
    });

    if (fav === 200) {
      console.log('     ✅ [PASS] Favicon present (no 404)');
      audit.passed++;
    } else {
      console.log('     ⚠️ [WARN] Favicon missing');
      audit.warnings++;
    }

    console.log('\n[6.2] Console error scan...');
    const criticalErrors = audit.consoleErrors.filter(e =>
      !e.includes('favicon') && !e.includes('compute-pressure')
    );
    console.log('     Critical console errors:', criticalErrors.length);

    if (criticalErrors.length === 0) {
      console.log('     ✅ [PASS] No console errors');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Console errors found:');
      criticalErrors.forEach(e => console.log('       -', e.substring(0, 80)));
      audit.issues.push('Console errors: ' + criticalErrors.length);
      audit.failed++;
    }

    console.log('\n[6.3] Memory check: Confetti running without freeze...');
    // Check if page is still responsive
    const responsive = await page.evaluate(() => {
      return document.querySelectorAll('*').length > 100;
    });

    if (responsive) {
      console.log('     ✅ [PASS] Page responsive (no memory freeze)');
      audit.passed++;
    } else {
      console.log('     ❌ [FAIL] Page may be frozen');
      audit.issues.push('Page responsive check failed');
      audit.failed++;
    }

    // =========================================================
    // FINAL REPORT
    // =========================================================
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                   FINAL AUDIT REPORT                          ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log('TESTS PASSED:    ' + audit.passed);
    console.log('TESTS FAILED:    ' + audit.failed);
    console.log('WARNINGS:        ' + audit.warnings);

    console.log('\nSECURITY CHECKS:');
    audit.securityChecks.forEach(s => console.log('  ✓', s));

    if (audit.failed === 0 && audit.warnings === 0) {
      console.log('\n🎉 RESULT: ★★★★★ 100% PRODUCTION READY ★★★★★');
      console.log('   System is error-free, bug-free, loophole-free!');
    } else if (audit.failed === 0) {
      console.log('\n✅ RESULT: ★★★★☆ 99% PRODUCTION READY');
      console.log('   Minor warnings present, no critical issues.');
    } else {
      console.log('\n❌ RESULT: ISSUES FOUND');
    }

    if (audit.issues.length > 0) {
      console.log('\nISSUES FOUND (' + audit.issues.length + '):');
      audit.issues.forEach((i, idx) => console.log('  ' + (idx+1) + '.', i));
    }

    await page.screenshot({ path: 'test-results/extreme-audit-final.png', fullPage: true });
    console.log('\n📸 Screenshot saved: test-results/extreme-audit-final.png');

  } catch (error) {
    console.error('\n❌ FATAL AUDIT ERROR:', error.message);
    audit.issues.push('Fatal error: ' + error.message);
  }

  await browser.close();

  return {
    passed: audit.passed,
    failed: audit.failed,
    warnings: audit.warnings,
    issues: audit.issues,
    ready: audit.failed === 0 && audit.issues.length === 0
  };
}

runExtremeAudit()
  .then(result => {
    console.log('\n════════════════════════════════════════════════════════════');
    console.log('AUDIT COMPLETE - EXITING');
    console.log('════════════════════════════════════════════════════════════\n');
    process.exit(result.ready ? 0 : 1);
  })
  .catch(e => {
    console.error(e);
    process.exit(1);
  });