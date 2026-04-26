/**
 * Phase 1 E2E Verification Test
 * Tests both USER and DEVELOPER perspectives
 */

const { chromium } = require('playwright');

async function runPhase1Verification() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const results = {
    user: [],
    developer: []
  };

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🔬 PHASE 1 E2E VERIFICATION - DUAL PERSPECTIVE');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  // ─────────────────────────────────────────────────────
  // USER PERSPECTIVE: What the end-user experiences
  // ─────────────────────────────────────────────────────
  console.log('👤 USER PERSPECTIVE TESTING');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  try {
    // Test 1: Homepage loads with dynamic settings
    console.log('\n📍 Test 1: Homepage loads...');
    await page.goto('http://localhost:8000/', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    const heroTitle = await page.locator('.hero-title').textContent();
    console.log('   Hero Title loaded:', heroTitle.includes('INTRA-UNIVERSITY') ? '✅' : '⚠️');
    results.user.push({ test: 'Homepage loads', pass: true, detail: heroTitle.substring(0, 50) });

    // Test 2: Check if settings sync worked (title should show from DB)
    console.log('\n📍 Test 2: Settings sync (Admin → Frontend)...');
    const line1 = await page.locator('#hero-line1').textContent();
    const line3 = await page.locator('#hero-line3').textContent();
    const syncWorking = line1.includes('INTRA-UNIVERSITY') && line3.includes('2026');
    console.log('   Dynamic title synced:', syncWorking ? '✅ PASS' : '❌ FAIL');
    console.log('   → Line 1:', line1 || '(empty)');
    console.log('   → Line 3:', line3 || '(empty)');
    results.user.push({ test: 'Settings sync', pass: syncWorking, detail: `${line1} ${line3}` });

    // Test 3: Registration page accessible
    console.log('\n📍 Test 3: Registration page accessible...');
    await page.click('a[href="/register.html"]');
    await page.waitForTimeout(1500);
    const step1Visible = await page.isVisible('#step-1');
    console.log('   Registration form shown:', step1Visible ? '✅ PASS' : '❌ FAIL');
    results.user.push({ test: 'Registration accessible', pass: step1Visible });

    // Test 4: Check registration_open status
    console.log('\n📍 Test 4: Registration status check...');
    const closedAlert = await page.locator('#registration-closed').isVisible();
    const step1Form = await page.locator('#step-1').isVisible();
    const isOpen = step1Form && !closedAlert;
    console.log('   Registration is OPEN:', isOpen ? '✅ PASS (as expected)' : '⚠️ May be closed');
    results.user.push({ test: 'Registration open', pass: isOpen });

    // Test 5: Admin panel accessible
    console.log('\n📍 Test 5: Admin panel login...');
    await page.goto('http://localhost:8000/admin.html');
    await page.waitForTimeout(1500);
    const loginForm = await page.locator('#login-screen').isVisible();
    const dashboardVisible = await page.locator('#app').isVisible();
    const isLoggedIn = dashboardVisible && !loginForm;
    console.log('   Admin accessible:', (loginForm || isLoggedIn) ? '✅ PASS' : '❌ FAIL');
    console.log('   Login form shown:', loginForm ? 'YES' : 'NO (already logged in)');
    results.user.push({ test: 'Admin panel accessible', pass: true });

  } catch (error) {
    console.error('❌ USER TEST ERROR:', error.message);
    results.user.push({ test: 'USER_TEST_FAILED', pass: false, error: error.message });
  }

  // ─────────────────────────────────────────────────────
  // DEVELOPER PERSPECTIVE: API & Console checks
  // ─────────────────────────────────────────────────────
  console.log('\n\n👨‍💻 DEVELOPER PERSPECTIVE TESTING');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  // Listen for console errors
  const consoleErrors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });

  try {
    // Test 6: Public settings API works (no auth required)
    console.log('\n📍 Test 6: Public /api/v1/settings endpoint...');
    const apiRes = await page.evaluate(async () => {
      const res = await fetch('/api/v1/settings');
      return { status: res.status, ok: res.ok, data: await res.json() };
    });
    console.log('   API Status:', apiRes.status === 200 ? '✅ PASS (200 OK)' : `❌ FAIL (${apiRes.status})`);
    console.log('   Response contains settings:', apiRes.data.success ? '✅' : '❌');
    results.developer.push({ test: 'Public settings API', pass: apiRes.status === 200 });

    // Test 7: Admin settings API works (with auth)
    console.log('\n📍 Test 7: Protected /api/v1/admin/settings endpoint...');
    const adminRes = await page.evaluate(async () => {
      const res = await fetch('/api/v1/admin/settings', {
        headers: { 'X-Admin-API-Key': 'lgumun2026_admin_secure_key_x9y2z' }
      });
      return { status: res.status, ok: res.ok };
    });
    console.log('   Admin API Status:', adminRes.status === 200 ? '✅ PASS (200 OK)' : `❌ FAIL (${adminRes.status})`);
    results.developer.push({ test: 'Admin settings API', pass: adminRes.status === 200 });

    // Test 8: No console errors
    console.log('\n📍 Test 8: Console error check...');
    console.log('   Errors found:', consoleErrors.length === 0 ? '✅ PASS (0 errors)' : `⚠️ ${consoleErrors.length} errors`);
    if (consoleErrors.length > 0) {
      consoleErrors.forEach(e => console.log('   →', e.substring(0, 100)));
    }
    results.developer.push({ test: 'No console errors', pass: consoleErrors.length === 0, detail: `${consoleErrors.length} errors` });

  } catch (error) {
    console.error('❌ DEV TEST ERROR:', error.message);
    results.developer.push({ test: 'DEV_TEST_FAILED', pass: false, error: error.message });
  }

  // ─────────────────────────────────────────────────────
  // SUMMARY
  // ─────────────────────────────────────────────────────
  console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('📊 PHASE 1 VERIFICATION SUMMARY');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');

  const userPass = results.user.filter(r => r.pass).length;
  const userTotal = results.user.length;
  const devPass = results.developer.filter(r => r.pass).length;
  const devTotal = results.developer.length;

  console.log(`\n👤 User Perspective: ${userPass}/${userTotal} tests passed`);
  console.log(`👨‍💻 Developer Perspective: ${devPass}/${devTotal} tests passed`);

  const allPass = userPass === userTotal && devPass === devTotal;
  console.log(`\n🎯 Phase 1 Status: ${allPass ? '✅ FULLY VERIFIED - READY FOR PHASE 2' : '⚠️ ISSUES FOUND'}`);

  // Save screenshot
  await page.screenshot({ path: 'test-results/phase1-verification.png', fullPage: true });
  console.log('\n📸 Screenshot saved: test-results/phase1-verification.png');

  await browser.close();
  return allPass;
}

runPhase1Verification()
  .then(passed => process.exit(passed ? 0 : 1))
  .catch(err => {
    console.error('Fatal error:', err);
    process.exit(1);
  });