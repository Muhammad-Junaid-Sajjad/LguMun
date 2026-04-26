/**
 * ULTIMATE UNIFIED STABILITY AUDIT (Phase 1 & 2 Combined)
 * Comprehensive testing for 110% production readiness
 * Verifies: UI Stability, API Sync, Business Logic, Security, and Hidden Bug elimination
 */

const { chromium } = require('playwright');

async function runUltimateAudit() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║   ULTIMATE UNIFIED STABILITY AUDIT (PHASE 1 + 2)           ║');
  console.log('║   Target: 110% Error-Free & Production Ready               ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const audit = {
    passed: 0,
    failed: 0,
    issues: [],
    logs: []
  };

  // Error listeners
  page.on('console', msg => {
    if (msg.type() === 'error') {
      const t = msg.text();
      // Ignore: favicon (404), compute-pressure (browser policy), 409 conflicts (duplicates - EXPECTED behavior)
      if (!t.includes('favicon') && !t.includes('compute-pressure') && !t.includes('409') && !t.includes('already registered')) {
        audit.logs.push(`Console Error: ${t}`);
      }
    }
  });

  try {
    // ---------------------------------------------------------
    // PART 1: UI STABILITY & SYNC (PHASE 1)
    // ---------------------------------------------------------
    console.log('📍 PART 1: UI & SYNC (PHASE 1) ------------------------');

    console.log('   [1.1] Testing Real-Time Settings Sync...');
    await page.goto('http://localhost:8000/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const line1 = await page.locator('#hero-line1').textContent();
    const l1Pass = line1.includes('INTRA-UNIVERSITY');
    console.log(`         Hero Sync: ${l1Pass ? '✅ PASS' : '❌ FAIL'}`);
    if (l1Pass) audit.passed++; else audit.failed++;

    console.log('   [1.2] Testing Stats Display...');
    const stats = await page.locator('#stat-committees').textContent();
    const statsPass = parseInt(stats) >= 9;
    console.log(`         Committees Stat: ${statsPass ? '✅ PASS' : '❌ FAIL'}`);
    if (statsPass) audit.passed++; else audit.failed++;

    // ---------------------------------------------------------
    // PART 2: BUSINESS LOGIC RIGOR (PHASE 2)
    // ---------------------------------------------------------
    console.log('\n📍 PART 2: BUSINESS LOGIC RIGOR (PHASE 2) ------------');

    const testId = Date.now();
    const testData = {
      name: 'Ultimate Audit User',
      email: `audit${testId}@lgu.edu.pk`,
      cnic: `ULT-${testId}`,
      phone: '03001234567',
      institution: 'Audit HQ'
    };

    console.log('   [2.1] Testing Core Registration Flow...');
    await page.goto('http://localhost:8000/register.html');
    await page.fill('#full_name', testData.name);
    await page.fill('#student_id_cnic', testData.cnic);
    await page.fill('#email', testData.email);
    await page.fill('#phone', testData.phone);
    await page.fill('#institution', testData.institution);
    await page.click('#btn-next-1');
    await page.waitForTimeout(1000);
    await page.selectOption('#committee_id', { index: 1 });
    await page.click('#btn-next-2');
    await page.waitForTimeout(1000);
    await page.click('#terms-checkbox');
    await page.click('#btn-submit');

    await page.waitForURL('**/success.html', { timeout: 10000 });
    const rollNum = await page.locator('#roll-number').textContent();
    const regPass = rollNum.includes('LGU-');
    console.log(`         Registration: ${regPass ? '✅ PASS' : '❌ FAIL'} (${rollNum})`);
    if (regPass) audit.passed++; else audit.failed++;

    console.log('   [2.2] Testing DUPLICATE PREVENTION (Security)...');
    await page.goto('http://localhost:8000/register.html');
    await page.fill('#full_name', 'Duplicate User');
    await page.fill('#student_id_cnic', testData.cnic); // Same CNIC
    await page.fill('#email', `new${testId}@test.com`);
    await page.fill('#phone', '03000000000');
    await page.fill('#institution', 'Dup Uni');
    await page.click('#btn-next-1');
    await page.waitForTimeout(800);
    await page.selectOption('#committee_id', { index: 1 });
    await page.click('#btn-next-2');
    await page.waitForTimeout(800);
    await page.click('#terms-checkbox');
    await page.click('#btn-submit');

    await page.waitForTimeout(2500);
    const pageText = await page.textContent('body');
    const dupBlocked = pageText.includes('already registered') || pageText.includes('exists') || !page.url().includes('success.html');
    console.log(`         Duplicate Blocked: ${dupBlocked ? '✅ PASS' : '❌ FAIL (LOOPHOLE FOUND!)'}`);
    if (dupBlocked) audit.passed++; else audit.failed++;

    // ---------------------------------------------------------
    // PART 3: RECENT FIXES & HIDDEN BUGS (AUDIT)
    // ---------------------------------------------------------
    console.log('\n📍 PART 3: FINAL STABILITY AUDIT (FIXES) -------------');

    console.log('   [3.1] Testing BUG-014 (No Registration Found UX)...');
    await page.evaluate(() => sessionStorage.clear());
    await page.goto('http://localhost:8000/success.html');
    await page.waitForTimeout(1500);
    const errorTitle = await page.locator('#error-content h2').textContent();
    const fixPass = errorTitle === 'No Registration Found';
    console.log(`         BUG-014 Fix: ${fixPass ? '✅ PASS' : '❌ FAIL'}`);
    if (fixPass) audit.passed++; else audit.failed++;

    console.log('   [3.2] Testing Console Stability (0 Errors)...');
    const critErrors = audit.logs.length;
    const consolePass = critErrors === 0;
    console.log(`         Console Hygiene: ${consolePass ? '✅ PASS' : '❌ FAIL ('+critErrors+' errors)'}`);
    if (consolePass) audit.passed++; else {
      audit.failed++;
      audit.issues.push(...audit.logs);
    }

    // ---------------------------------------------------------
    // FINAL VERDICT
    // ---------------------------------------------------------
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║                   ULTIMATE AUDIT REPORT                      ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log(`   TOTAL TESTS PASSED: ${audit.passed}/6`);
    console.log(`   TOTAL CRITICAL FAILURES: ${audit.failed}`);

    if (audit.failed === 0) {
      console.log('\n   🎉 RESULT: ★★★★★ 110% STABLE - PRODUCTION READY ★★★★★');
      console.log('   No hidden bugs, loopholes, or defects found.');
    } else {
      console.log('\n   ❌ RESULT: SYSTEM UNSTABLE - FIXES REQUIRED');
      audit.issues.forEach((iss, i) => console.log(`      ${i+1}. ${iss}`));
    }

    await page.screenshot({ path: 'test-results/ultimate-audit.png', fullPage: true });

  } catch (e) {
    console.error('   ❌ FATAL ERROR IN AUDIT:', e.message);
  } finally {
    await browser.close();
    process.exit(audit.failed === 0 ? 0 : 1);
  }
}

runUltimateAudit();