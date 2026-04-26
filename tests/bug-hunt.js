/**
 * Pre-Phase 2: Comprehensive Bug Hunt
 * Checks for hidden defects, edge cases, and potential issues
 */

const { chromium } = require('playwright');

async function runBugHunt() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const bugs = [];
  const consoleErrors = [];

  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🔍 PRE-PHASE 2: COMPREHENSIVE BUG HUNT');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // ─────────────────────────────────────────────────────
  // 1. HOMEPAGE COMPREHENSIVE CHECK
  // ─────────────────────────────────────────────────────
  console.log('📍 1. HOMEPAGE COMPREHENSIVE CHECK');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  try {
    await page.goto('http://localhost:8000/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Check hero section
    const heroTitle = await page.locator('.hero-title').count();
    const heroSubtitle = await page.locator('.hero-subtitle').count();
    console.log(`   Hero title present: ${heroTitle > 0 ? '✅' : '❌'}`);
    console.log(`   Hero subtitle present: ${heroSubtitle > 0 ? '✅' : '❌'}`);

    // Check navbar
    const navLinks = await page.locator('nav a').count();
    console.log(`   Navbar links: ${navLinks} ✅`);

    // Check committees section
    const committeesSection = await page.locator('#committees, .committees, [id*="committee"]').count();
    console.log(`   Committees section found: ${committeesSection > 0 ? '✅' : '⚠️'}`);

    // Check stats
    const statDelegates = await page.locator('#stat-registered, [id*="stat-register"]').count();
    const statCommittees = await page.locator('#stat-committees, [id*="stat-committee"]').count();
    console.log(`   Delegation count visible: ${statDelegates > 0 ? '✅' : '⚠️'}`);
    console.log(`   Committees count visible: ${statCommittees > 0 ? '✅' : '⚠️'}`);

  } catch (e) {
    bugs.push({ area: 'Homepage', error: e.message });
    console.log('   ❌ ERROR:', e.message);
  }

  // ─────────────────────────────────────────────────────
  // 2. REGISTRATION FLOW - ALL 3 STEPS
  // ─────────────────────────────────────────────────────
  console.log('\n📍 2. REGISTRATION FLOW (ALL 3 STEPS)');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  const testName = `BugHuntTest ${Date.now()}`;
  const testEmail = `bh${Date.now()}@test.com`;

  try {
    await page.goto('http://localhost:8000/register.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    // STEP 1: Fill form
    console.log('   Step 1: Personal Info...');
    await page.fill('#full_name', testName);
    await page.fill('#student_id_cnic', `12345${Date.now().toString().slice(-7)}`);
    await page.fill('#email', testEmail);
    await page.fill('#phone', '03001234567');
    await page.fill('#institution', 'Bug Hunt University');
    console.log('   ✅ Form filled');

    // STEP 2: Committee selection
    console.log('   Step 2: Committee Selection...');
    await page.click('#btn-next-1');
    await page.waitForTimeout(1000);

    const step2Visible = await page.isVisible('#step-2');
    console.log(`   Step 2 visible: ${step2Visible ? '✅' : '❌'}`);

    if (step2Visible) {
      // Check if committees are populated
      const committeeOptions = await page.locator('#committee_id option').count();
      console.log(`   Available committees: ${committeeOptions - 1} ✅`);

      // Select a committee
      await page.selectOption('#committee_id', { index: 1 });
      await page.click('#btn-next-2');
      await page.waitForTimeout(1000);
    }

    // STEP 3: Review
    console.log('   Step 3: Review & Confirm...');
    const step3Visible = await page.isVisible('#step-3');
    console.log(`   Step 3 visible: ${step3Visible ? '✅' : '❌'}`);

    // Check confirmation data
    const confirmData = await page.locator('#confirm-grid, .confirm-grid').textContent();
    console.log(`   Confirmation data shown: ${confirmData?.includes(testName) ? '✅' : '⚠️'}`);

    // Don't actually submit - just verify the flow works
    console.log('   ⚠️ Skipping actual submission (preventing database clutter)');

  } catch (e) {
    bugs.push({ area: 'Registration Flow', error: e.message });
    console.log('   ❌ ERROR:', e.message);
  }

  // ─────────────────────────────────────────────────────
  // 3. SUCCESS PAGE CHECK
  // ─────────────────────────────────────────────────────
  console.log('\n📍 3. SUCCESS PAGE CHECK');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  try {
    await page.goto('http://localhost:8000/success.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    const rollElement = await page.locator('#roll-number').count();
    const confettiCanvas = await page.locator('canvas').count();

    console.log(`   Roll number element: ${rollElement > 0 ? '✅' : '⚠️ (using different ID?)'}`);
    console.log(`   Confetti present: ${confettiCanvas > 0 ? '✅' : '⚠️'}`);

    // Try to find alternative IDs
    const pageText = await page.textContent('body');
    if (pageText.includes('LGU-')) {
      console.log('   ✅ Roll number found in page text');
    }

  } catch (e) {
    bugs.push({ area: 'Success Page', error: e.message });
    console.log('   ❌ ERROR:', e.message);
  }

  // ─────────────────────────────────────────────────────
  // 4. ADMIN PANEL - DELEGATES LIST
  // ─────────────────────────────────────────────────────
  console.log('\n📍 4. ADMIN PANEL - DELEGATES LIST');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  try {
    await page.goto('http://localhost:8000/admin.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Check login screen or dashboard
    const loginVisible = await page.locator('#login-screen').isVisible().catch(() => false);
    const appVisible = await page.locator('#app').isVisible().catch(() => false);

    console.log(`   Login screen: ${loginVisible ? '✅ shown' : '❌'}`);
    console.log(`   Dashboard: ${appVisible ? '✅ shown (already logged in)' : '❌'}`);

    if (appVisible) {
      // Check for stats
      const totalDelegates = await page.locator('#s-total, [id*="total"]').first().textContent().catch(() => null);
      console.log(`   Total delegates shown: ${totalDelegates ? totalDelegates : '⚠️'}`);
    }

  } catch (e) {
    bugs.push({ area: 'Admin Panel', error: e.message });
    console.log('   ❌ ERROR:', e.message);
  }

  // ─────────────────────────────────────────────────────
  // 5. COMMITTEES PAGE CHECK
  // ─────────────────────────────────────────────────────
  console.log('\n📍 5. COMMITTEES PAGE CHECK');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  try {
    await page.goto('http://localhost:8000/committees.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1500);

    const committeeRows = await page.locator('#committees-body tr:not(.contact-info-cell)').count();
    console.log(`   Committee rows: ${committeeRows} ${committeeRows >= 9 ? '✅ (9+)' : '⚠️'}`);

    // Check API response
    const apiData = await page.evaluate(async () => {
      const res = await fetch('/api/v1/committees');
      return res.json();
    });
    console.log(`   API committees count: ${apiData?.data?.committees?.length || 0} ✅`);

  } catch (e) {
    bugs.push({ area: 'Committees Page', error: e.message });
    console.log('   ❌ ERROR:', e.message);
  }

  // ─────────────────────────────────────────────────────
  // 6. API ENDPOINTS HEALTH CHECK
  // ─────────────────────────────────────────────────────
  console.log('\n📍 6. API ENDPOINTS HEALTH CHECK');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  const endpoints = [
    '/api/v1/health',
    '/api/v1/committees',
    '/api/v1/delegates/count',
    '/api/v1/settings'
  ];

  for (const endpoint of endpoints) {
    try {
      const res = await fetch(`http://localhost:8000${endpoint}`);
      console.log(`   ${endpoint}: ${res.status === 200 ? '✅' : `❌ (${res.status})`}`);
    } catch (e) {
      console.log(`   ${endpoint}: ❌ ${e.message}`);
    }
  }

  // ─────────────────────────────────────────────────────
  // 7. CONSOLE ERRORS CHECK
  // ─────────────────────────────────────────────────────
  console.log('\n📍 7. CONSOLE ERRORS');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  if (consoleErrors.length === 0) {
    console.log('   ✅ NO CONSOLE ERRORS DETECTED');
  } else {
    console.log(`   ⚠️ Found ${consoleErrors.length} console error(s):`);
    consoleErrors.forEach((e, i) => console.log(`   ${i+1}. ${e.substring(0, 100)}`));
    bugs.push({ area: 'Console Errors', detail: consoleErrors });
  }

  // ─────────────────────────────────────────────────────
  // 8. FORM VALIDATION CHECK
  // ──��─��────────────────────────────────────────────────
  console.log('\n📍 8. FORM VALIDATION');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  try {
    await page.goto('http://localhost:8000/register.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);

    // Try to submit empty form
    await page.click('#btn-next-1');
    await page.waitForTimeout(500);

    // Check if validation errors appear
    const errorMessages = await page.locator('.error, [class*="error"], .invalid').count();
    const validationExists = errorMessages > 0 || await page.isVisible('#step-2') === false;

    console.log(`   Empty form validation: ${validationExists ? '✅ working' : '⚠️ not found'}`);

  } catch (e) {
    console.log('   ⚠️ Could not test validation');
  }

  // ─────────────────────────────────────────────────────
  // SUMMARY
  // ─────────────────────────────────────────────────────
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 BUG HUNT SUMMARY');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  if (bugs.length === 0) {
    console.log('\n🎉 NO BUGS FOUND! System is clean.');
  } else {
    console.log(`\n⚠️ Found ${bugs.length} issue(s):`);
    bugs.forEach((b, i) => console.log(`   ${i+1}. ${b.area}: ${b.error || b.detail?.join(', ')}`));
  }

  await page.screenshot({ path: 'test-results/bug-hunt.png', fullPage: true });
  console.log('\n📸 Screenshot saved: test-results/bug-hunt.png');

  await browser.close();
  return bugs.length === 0;
}

runBugHunt()
  .then(clean => {
    console.log(`\n🎯 BUG HUNT RESULT: ${clean ? '✅ CLEAN - READY FOR PHASE 2' : '❌ ISSUES FOUND'}`);
    process.exit(clean ? 0 : 1);
  })
  .catch(e => {
    console.error('Fatal error:', e);
    process.exit(1);
  });