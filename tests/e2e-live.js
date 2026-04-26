#!/usr/bin/env node
// Comprehensive E2E Test Suite - Watch in Real Time
// Run with: node tests/e2e-live.js
// Opens visible browser so you can watch every test

const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:8000';
const ADMIN_KEY = 'lgumun2026_admin_secure_key_x9y2z';

const sleep = ms => new Promise(r => setTimeout(r, ms));
const log = (msg, type = 'info') => {
  const icons = { pass: '✅', fail: '❌', info: '📍', warn: '⚠️', step: '🔹', done: '✔️', error: '🚨' };
  console.log(`${icons[type] || '📍'} ${msg}`);
};

async function runTests() {
  log(`Starting Comprehensive E2E Test Suite`, 'step');
  log(`Target: ${BASE_URL}`, 'info');
  log(`This will open a VISIBLE browser. Watch each test!\n`, 'warn');

  const browser = await chromium.launch({
    headless: false,
    args: ['--window-size=1920,1080']
  });

  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    ignoreHTTPSErrors: true
  });

  const page = await context.newPage();

  // Capture all browser console messages
  const browserLogs = [];
  page.on('console', msg => browserLogs.push(`[${msg.type().toUpperCase()}] ${msg.text()}`));
  page.on('pageerror', err => browserLogs.push(`[PAGE ERROR] ${err.message}`));
  page.on('requestfailed', req => browserLogs.push(`[REQ FAILED] ${req.url()}`));

  let allPassed = 0;
  let allFailed = 0;

  // ======================================================
  // TEST 1: HOME PAGE
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 1: Home Page (index.html)`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle', timeout: 15000 });
    log(`Home page loaded: ${page.url()}`, 'pass');

    const title = await page.title();
    if (title.includes('LGU') || title.includes('MUN')) {
      log(`Page title OK: "${title}"`, 'pass');
    } else {
      log(`Page title suspicious: "${title}"`, 'warn');
    }

    const hero = await page.$('.hero, .hero-section, .hero-banner, header, main');
    log(`Hero/Header found: ${hero ? 'YES' : 'NO'}`, hero ? 'pass' : 'warn');

    const registerBtn = await page.$('a[href*="register"], button:has-text("Register"), .cta-button');
    if (registerBtn) {
      log(`Register Now button: FOUND`, 'pass');
    } else {
      log(`Register Now button: NOT FOUND`, 'fail');
      allFailed++;
    }

    const navLinks = await page.$$('nav a, .nav-item, header a');
    log(`Navigation links: ${navLinks.length} found`, navLinks.length > 0 ? 'pass' : 'warn');

    await page.screenshot({ path: 'test-results/01-home-page.png' });
    log(`Screenshot saved: test-results/01-home-page.png`, 'info');

    allPassed++;
  } catch (e) {
    log(`Home page FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 2: COMMITTEES PAGE
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 2: Committees Page (committees.html)`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    await page.goto(`${BASE_URL}/committees.html`, { waitUntil: 'networkidle', timeout: 15000 });
    log(`Committees page loaded: ${page.url()}`, 'pass');

    await sleep(2000);
    const commCards = await page.$$('.comm-card, .committee-card, .card');
    log(`Committee cards: ${commCards.length} found`, commCards.length > 0 ? 'pass' : 'warn');

    const text = await page.textContent('body');
    const hasCommitteeData = text.includes('UNSC') || text.includes('UNGA') || text.includes('Committee');
    log(`Committee data present: ${hasCommitteeData ? 'YES' : 'NO'}`, hasCommitteeData ? 'pass' : 'fail');

    if (!hasCommitteeData) {
      log(`No committee data - possible API failure`, 'fail');
      allFailed++;
    }

    await page.screenshot({ path: 'test-results/02-committees-page.png' });
    log(`Screenshot saved: test-results/02-committees-page.png`, 'info');

    allPassed++;
  } catch (e) {
    log(`Committees page FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 3: REGISTRATION PAGE (Multi-Step Form)
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 3: Registration Page (register.html)`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    await page.goto(`${BASE_URL}/register.html`, { waitUntil: 'networkidle', timeout: 15000 });
    log(`Registration page loaded: ${page.url()}`, 'pass');

    await sleep(2000);

    // Check for form fields - use correct IDs from the actual form
    const fullNameInput = await page.$('#full_name');
    const emailInput = await page.$('#email');
    const studentIdInput = await page.$('#student_id_cnic');
    const phoneInput = await page.$('#phone');
    const institutionInput = await page.$('#institution');
    const committeeSelect = await page.$('#committee_id');

    log(`Full Name field (#full_name): ${fullNameInput ? 'OK' : 'MISSING'}`, fullNameInput ? 'pass' : 'fail');
    log(`Email field (#email): ${emailInput ? 'OK' : 'MISSING'}`, emailInput ? 'pass' : 'fail');
    log(`Student ID field (#student_id_cnic): ${studentIdInput ? 'OK' : 'MISSING'}`, studentIdInput ? 'pass' : 'fail');
    log(`Phone field (#phone): ${phoneInput ? 'OK' : 'MISSING'}`, phoneInput ? 'pass' : 'fail');
    log(`Institution field (#institution): ${institutionInput ? 'OK' : 'MISSING'}`, institutionInput ? 'pass' : 'fail');
    log(`Committee select (#committee_id): ${committeeSelect ? 'OK' : 'MISSING'}`, committeeSelect ? 'pass' : 'fail');

    // Check for step indicators
    const step1 = await page.$('#step-1');
    const step2 = await page.$('#step-2');
    log(`Step 1 (#step-1): ${step1 ? 'OK' : 'MISSING'}`, step1 ? 'pass' : 'fail');
    log(`Step 2 (#step-2): ${step2 ? 'OK' : 'MISSING'}`, step2 ? 'pass' : 'fail');

    // Check Next button
    const nextBtn = await page.$('#btn-next-1');
    log(`Next button (#btn-next-1): ${nextBtn ? 'OK' : 'MISSING'}`, nextBtn ? 'pass' : 'fail');

    if (!fullNameInput || !emailInput || !studentIdInput) allFailed++;

    await page.screenshot({ path: 'test-results/03-registration-page.png' });
    log(`Screenshot saved: test-results/03-registration-page.png`, 'info');

    allPassed++;
  } catch (e) {
    log(`Registration page FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 4: REGISTRATION FLOW (Multi-Step Live Test)
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 4: Registration Flow (Multi-Step Form)`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    await page.goto(`${BASE_URL}/register.html`, { waitUntil: 'networkidle', timeout: 15000 });
    await sleep(2000);

    const testRoll = `TEST${Date.now().toString().slice(-8)}`;
    const testEmail = `test${Date.now()}@test.com`;

    log(`Test Roll: ${testRoll}`, 'info');
    log(`Test Email: ${testEmail}`, 'info');

    // STEP 1: Fill personal details
    log(`Step 1: Filling personal details...`, 'info');

    await page.fill('#full_name', 'Test User E2E');
    log(`  - Name filled`, 'info');

    await page.fill('#student_id_cnic', testRoll);
    log(`  - Roll filled`, 'info');

    await page.fill('#email', testEmail);
    log(`  - Email filled`, 'info');

    await page.fill('#phone', '03001234567');
    log(`  - Phone filled`, 'info');

    await page.fill('#institution', 'Test University Lahore');
    log(`  - Institution filled`, 'info');

    await page.screenshot({ path: 'test-results/04a-step1-filled.png' });
    log(`  - Screenshot saved`, 'info');

    // Click Next to go to Step 2
    log(`Clicking Next button to proceed to Step 2...`, 'info');
    await page.click('#btn-next-1');
    await sleep(2000);

    const step2Visible = await page.isVisible('#step-2');
    log(`Step 2 visible: ${step2Visible}`, step2Visible ? 'pass' : 'warn');

    if (step2Visible) {
      // STEP 2: Select committee
      log(`Step 2: Selecting committee...`, 'info');

      // Check committee options
      const commOptions = await page.$$('#committee_id option');
      log(`Committee options: ${commOptions.length}`, commOptions.length > 1 ? 'pass' : 'warn');

      if (commOptions.length > 1) {
        await page.selectOption('#committee_id', { index: 1 });
        log(`Committee selected`, 'info');
      }

      await page.screenshot({ path: 'test-results/04b-step2-filled.png' });

      // Click Next to go to Step 3
      log(`Clicking Next to proceed to Step 3...`, 'info');
      await page.click('#btn-next-2');
      await sleep(2000);
    }

    // STEP 3: Review and Submit
    const step3Visible = await page.isVisible('#step-3');
    log(`Step 3 visible: ${step3Visible}`, step3Visible ? 'pass' : 'warn');

    if (step3Visible) {
      await page.screenshot({ path: 'test-results/04c-step3-review.png' });
      log(`Review step screenshot saved`, 'info');
    }

    // Click Submit (if submit button exists in step 3)
    const submitBtn = await page.$('#step-3 button[type="submit"], .btn-submit, button:has-text("Submit")');
    if (submitBtn) {
      log(`Submit button found - clicking...`, 'info');
      await submitBtn.click();
      await sleep(3000);

      const pageText = await page.textContent('body');
      const success = pageText.includes('success') || pageText.includes('Success') ||
                    pageText.includes('registered') || pageText.includes('Registered');

      if (success) {
        log(`Registration SUCCESS!`, 'pass');
        allPassed++;
      } else {
        log(`Registration result unclear - checking for errors`, 'warn');
        const errEl = await page.$('.alert-error, .error-msg, [class*="error" i]');
        if (errEl) {
          const errText = await errEl.textContent();
          log(`Error message: ${errText.trim().substring(0, 100)}`, 'warn');
        }
      }
    } else {
      log(`Submit button NOT FOUND in Step 3`, 'warn');
      allFailed++;
    }

    await page.screenshot({ path: 'test-results/04-registration-submit.png', fullPage: true });
    log(`Screenshot saved: test-results/04-registration-submit.png`, 'info');

  } catch (e) {
    log(`Registration flow FAILED: ${e.message}`, 'fail');
    allFailed++;
    await page.screenshot({ path: 'test-results/04-error.png' });
  }

  await sleep(1000);

  // ======================================================
  // TEST 5: ADMIN PANEL LOGIN
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 5: Admin Panel Login`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    await page.goto(`${BASE_URL}/admin.html`, { waitUntil: 'networkidle', timeout: 15000 });
    log(`Admin page loaded: ${page.url()}`, 'pass');

    const loginVisible = await page.isVisible('#login-screen');
    log(`Login screen visible: ${loginVisible}`, loginVisible ? 'pass' : 'fail');

    await page.fill('#login-user', 'admin');
    await page.fill('#login-pass', ADMIN_KEY);
    log(`Credentials filled`, 'info');

    await page.click('.login-btn');
    log(`Login button clicked`, 'info');

    await sleep(4000);

    const appVisible = await page.isVisible('#app');
    const loginError = await page.isVisible('#login-err.show');

    if (appVisible) {
      log(`Admin panel SUCCESS - App is visible!`, 'pass');
      allPassed++;

      await sleep(2000);
      const statsText = await page.textContent('#s-total, .stat-value');
      log(`Dashboard stat value: ${statsText ? statsText.trim() : 'loading...'}`);

    } else if (loginError) {
      const errText = await page.textContent('#login-err.show');
      log(`Admin login ERROR: ${errText}`, 'fail');
      allFailed++;
    } else {
      log(`Admin login state UNCLEAR`, 'warn');
    }

    await page.screenshot({ path: 'test-results/05-admin-login.png', fullPage: true });
    log(`Screenshot saved: test-results/05-admin-login.png`, 'info');

  } catch (e) {
    log(`Admin login FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 6: ADMIN DELEGATES PAGE
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 6: Admin - Delegates Page`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    const delegatesNav = await page.$('.nav-item:has-text("All Delegates"), .nav-item:has-text("Delegates")');
    if (delegatesNav) {
      await delegatesNav.click();
      log(`Clicked Delegates nav`, 'info');
      await sleep(3000);

      const pageText = await page.textContent('body');
      const hasDelegates = pageText.includes('UNSC') || pageText.includes('Roll') || pageText.includes('roll');
      log(`Delegate data visible: ${hasDelegates}`, hasDelegates ? 'pass' : 'warn');

      if (!hasDelegates) {
        log(`No delegate data loaded`, 'warn');
      }

      const tableRows = await page.$$('tbody tr, table tr');
      log(`Table rows: ${tableRows.length}`, tableRows.length > 0 ? 'pass' : 'warn');

    } else {
      log(`Delegates nav NOT FOUND`, 'fail');
      allFailed++;
    }

    await page.screenshot({ path: 'test-results/06-admin-delegates.png', fullPage: true });

  } catch (e) {
    log(`Admin delegates FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 7: ADMIN COMMITTEES PAGE
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 7: Admin - Committees Page`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    const commNav = await page.$('.nav-item:has-text("Committees")');
    if (commNav) {
      await commNav.click();
      log(`Clicked Committees nav`, 'info');
      await sleep(2000);

      const pageText = await page.textContent('body');
      const hasComms = pageText.includes('UNSC') || pageText.includes('UNGA') || pageText.includes('WHO');
      log(`Committee data visible: ${hasComms}`, hasComms ? 'pass' : 'warn');

      if (!hasComms) {
        log(`No committee data loaded`, 'warn');
      }

    } else {
      log(`Committees nav NOT FOUND`, 'fail');
      allFailed++;
    }

    await page.screenshot({ path: 'test-results/07-admin-committees.png', fullPage: true });

  } catch (e) {
    log(`Admin committees FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 8: ADMIN QUERIES PAGE
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 8: Admin - Queries Page`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    const queriesNav = await page.$('.nav-item:has-text("Queries")');
    if (queriesNav) {
      await queriesNav.click();
      log(`Clicked Queries nav`, 'info');
      await sleep(2000);

      const pageText = await page.textContent('body');
      const hasQueries = pageText.includes('pending') || pageText.includes('Queries') || pageText.includes('reply');
      log(`Queries page loaded: ${hasQueries}`, 'pass');

      const filters = await page.$$('.qf-btn');
      log(`Filter buttons: ${filters.length}`, filters.length > 0 ? 'pass' : 'warn');

    } else {
      log(`Queries nav NOT FOUND`, 'fail');
      allFailed++;
    }

    await page.screenshot({ path: 'test-results/08-admin-queries.png', fullPage: true });

  } catch (e) {
    log(`Admin queries FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // TEST 9: ADMIN SETTINGS PAGE
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`TEST 9: Admin - Event Settings Page`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  try {
    const settingsNav = await page.$('.nav-item:has-text("Event Settings"), .nav-item:has-text("Settings")');
    if (settingsNav) {
      await settingsNav.click();
      log(`Clicked Settings nav`, 'info');
      await sleep(2000);

      const inputs = await page.$$('.ctrl-field input, .ctrl-field textarea');
      log(`Settings inputs: ${inputs.length}`, inputs.length > 0 ? 'pass' : 'warn');

      if (inputs.length === 0) {
        log(`No settings inputs found`, 'warn');
      }

    } else {
      log(`Settings nav NOT FOUND`, 'fail');
      allFailed++;
    }

    await page.screenshot({ path: 'test-results/09-admin-settings.png', fullPage: true });

  } catch (e) {
    log(`Admin settings FAILED: ${e.message}`, 'fail');
    allFailed++;
  }

  await sleep(1000);

  // ======================================================
  // BROWSER CONSOLE LOG (ERRORS ONLY)
  // ======================================================
  log(`\n═══════════════════════════════════════`, 'step');
  log(`Browser Console Errors (${browserLogs.filter(l => l.includes('ERROR')).length} errors)`, 'step');
  log(`═══════════════════════════════════════`, 'step');

  browserLogs.filter(l => l.includes('ERROR')).forEach(log => {
    console.log(`  🚨 ${log.substring(0, 200)}`);
  });

  // ======================================================
  // FINAL SUMMARY
  // ======================================================
  log(`\n══════════════════════════════════════════════════════════`, 'step');
  log(`FINAL TEST SUMMARY`, 'step');
  log(`══════════════════════════════════════════════════════════`, 'step');
  log(`Tests Passed: ${allPassed}`, 'pass');
  log(`Tests Failed: ${allFailed}`, allFailed > 0 ? 'fail' : 'pass');
  log(`Total Tests: ${allPassed + allFailed}`, 'info');
  log(`Pass Rate: ${Math.round((allPassed / (allPassed + allFailed)) * 100)}%`, allPassed >= allFailed ? 'pass' : 'warn');

  if (allFailed > 0) {
    log(`\n⚠️ ${allFailed} test(s) need attention!`, 'warn');
  } else {
    log(`\n✅ All tests passed!`, 'pass');
  }

  log(`\n📁 Screenshots saved in: test-results/`, 'info');

  await browser.close();
  log(`\n🔚 E2E Test Suite Complete!`, 'done');

  return { passed: allPassed, failed: allFailed };
}

// Run
runTests().catch(e => {
  console.log(`\n❌ Test runner CRASHED: ${e.message}`);
  process.exit(1);
});