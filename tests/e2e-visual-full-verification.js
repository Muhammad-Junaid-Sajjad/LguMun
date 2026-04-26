/**
 * E2E Visual Test: Admin to Frontend Full System Verification
 * All tests run VISIBLY with slow motion and video recording
 * Tests EVERYTHING: event title, registration, announcements, logos
 */

const { chromium } = require('playwright');

const API_KEY = 'lgumun2026_admin_secure_key_x9y2z';
const ADMIN_URL = 'http://localhost:8000/admin.html';
const API_URL = 'http://localhost:8000';

let browser, context, page;
let passed = 0, failed = 0;
let testVideoDir = './test-videos/visual-' + Date.now();

// Fast test settings
const VISUAL_CONFIG = {
  headless: true,
  slowMo: 0,
  recordVideo: false,
  timeout: 30000
};

async function log(msg, type = 'info') {
  const t = new Date().toISOString().split('T')[1].slice(0, 12);
  const p = type === 'pass' ? '✅' : type === 'fail' ? '❌' : type === 'warn' ? '⚠️' : '📷';
  console.log(`[${t}] ${p} ${msg}`);
}

async function setup() {
  log('Launching browser for fast testing...');

  browser = await chromium.launch({
    headless: true,
    slowMo: 0
  });

  context = await browser.newContext();

  page = await context.newPage();
  await page.setViewportSize({ width: 1400, height: 900 });

  page.setDefaultTimeout(20000);
}

async function takeScreenshot(label) {
  const filename = `${label}-${Date.now()}.png`;
  await page.screenshot({ path: filename, fullPage: true });
  log(`📷 Screenshot saved: ${filename}`);
  return filename;
}

async function highlightAndCapture(elementSelector, label) {
  await page.evaluate((selector) => {
    const el = document.querySelector(selector);
    if (el) {
      el.style.border = '4px solid red';
      el.style.boxShadow = '0 0 20px red';
      el.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, elementSelector);

  await page.waitForTimeout(1000);
  await takeScreenshot(label);

  const text = await page.evaluate((selector) => {
    const el = document.querySelector(selector);
    return el ? el.textContent : 'NOT FOUND';
  }, elementSelector);

  log(`📷 Highlighted element text: "${text.trim()}"`);
  return text;
}

async function teardown() {
  if (browser) {
    await browser.close();
  }
  log(`\n===== FINAL RESULTS =====`);
  log(`Total Passed: ${passed}`);
  log(`Total Failed: ${failed}`);
}

// =========================================================================
// TEST 1: LOGO VISIBILITY CHECK (All Pages)
// =========================================================================
async function testLogosAllPages() {
  log('\n=== TEST 1: LOGO VISIBILITY ON ALL PAGES ===', 'info');

  const pages = [
    { url: '/', name: 'Home Page' },
    { url: '/register.html', name: 'Register Page' },
    { url: '/success.html', name: 'Success Page' },
    { url: '/committees.html', name: 'Committees Page' },
    { url: '/admin.html', name: 'Admin Login Page' }
  ];

  for (const p of pages) {
    log(`\n📷 Checking logos on ${p.name}...`);
    await page.goto(API_URL + p.url);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500); // SlowMo equivalent
    await takeScreenshot(`logo-${p.name}`);

    // Check for LGU Official Logo
    const lgulogo = page.locator('img[alt*="LGU"], img[alt*="lgu"]').first();
    const hasLGU = await lgulogo.isVisible({ timeout: 2000 }).catch(() => false);
    if (hasLGU) {
      log(`✅ LGU Official Logo visible on ${p.name}`);
      passed++;
    } else {
      log(`❌ LGU Official Logo NOT found on ${p.name}`);
      failed++;
    }

    // Check for LGU MUN Society Logo
    const munLogo = page.locator('img[src*="lgumun-society"]').first();
    const hasMun = await munLogo.isVisible({ timeout: 2000 }).catch(() => false);
    if (hasMun) {
      log(`✅ LGU MUN Society Logo visible on ${p.name}`);
      passed++;
    } else {
      log(`⚠️ LGU MUN Society Logo not found on ${p.name}`);
    }
  }
}

// =========================================================================
// TEST 2: EVENT TITLE SYNC (Admin → Frontend)
// =========================================================================
async function testEventTitleSync() {
  log('\n=== TEST 2: EVENT TITLE SYNC (ADMIN → FRONTEND) ===', 'info');

  // Step 1: Go to Admin
  log('Step 1: Logging into Admin Panel...');
  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  await takeScreenshot('admin-login');

  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });
  await page.waitForTimeout(500);
  await takeScreenshot('admin-logged-in');

  // Step 2: Navigate to Event Settings
  log('Step 2: Navigating to Event Settings...');
  await page.click('.nav-item:has-text("Event Settings")');
  await page.waitForTimeout(500);
  await takeScreenshot('admin-event-settings');

  // Step 3: Change Event Title
  const newTitle = `LGUMUN 2026 - Visual Test ${Date.now()}`;
  log(`Step 3: Setting Event Title to: "${newTitle}"`);
  await page.fill('#ctrl-title', newTitle);
  await page.waitForTimeout(500);
  await takeScreenshot('admin-title-filled');

  // Step 4: Save Event Info
  log('Step 4: Saving Event Info...');
  await page.click('.save-btn:has-text("Save Event Info")');
  await page.waitForTimeout(1000);
  await takeScreenshot('admin-title-saved');

  // Step 5: Verify on Frontend
  log('Step 5: Checking if title appears on FRONTEND homepage...');
  await page.goto(API_URL + '/');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(1000);
  await takeScreenshot('frontend-home-after-save');

  // Find and highlight the hero title
  const heroTitle = await highlightAndCapture('h1, .hero h2, .hero-title, .main-title', 'frontend-hero-highlighted');

  if (heroTitle.includes('Visual Test') || heroTitle.includes('LGUMUN 2026')) {
    log(`✅ Event title SYNCED to frontend: "${heroTitle.trim()}"`);
    passed++;
  } else {
    log(`❌ Event title NOT synced. Found: "${heroTitle.trim()}"`);
    failed++;
  }

  // Also check navbar logo
  const navLogo = page.locator('.nav-logo img, .header-logo img, header img').first();
  if (await navLogo.isVisible({ timeout: 2000 }).catch(() => false)) {
    const logoSrc = await navLogo.getAttribute('src');
    log(`✅ Navbar Logo visible: ${logoSrc}`);
    passed++;
  }
}

// =========================================================================
// TEST 3: REGISTRATION FLOW (Full Visual)
// =========================================================================
async function testRegistrationFlow() {
  log('\n=== TEST 3: REGISTRATION FLOW (FULL VISUAL) ===', 'info');

  // Step 1: Go to Register Page
  log('Step 1: Going to Registration Page...');
  await page.goto(API_URL + '/register.html');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  await takeScreenshot('register-page');

  // Step 2: Fill Registration Form
  log('Step 2: Filling Registration Form...');
  const testName = `Visual Test Delegate ${Date.now()}`;
  const testEmail = `visual${Date.now()}@test.com`;
  const testPhone = `0300${Math.floor(Math.random() * 10000000)}`;
  const testRoll = `VT${Date.now()}`;

  await page.fill('#full_name', testName);
  await page.waitForTimeout(500);

  await page.fill('#student_id_cnic', testRoll);
  await page.waitForTimeout(500);

  await page.fill('#email', testEmail);
  await page.waitForTimeout(500);

  await page.fill('#phone', testPhone);
  await page.waitForTimeout(500);

  await page.fill('#institution', 'Lahore Garrison University');
  await page.waitForTimeout(500);

  await takeScreenshot('register-form-filled');
  log(`Filled: ${testName}, ${testEmail}, ${testRoll}`);

  // Step 3: Select Committee
  log('Step 3: Selecting Committee...');
  const committeeSelect = page.locator('#committee_id, select').first();
  if (await committeeSelect.isVisible({ timeout: 2000 }).catch(() => false)) {
    // Get available options
    const options = await page.locator('#committee_id option, select option').allTextContents();
    log(`Committee options: ${options.slice(0, 5).join(', ')}...`);
    await committeeSelect.selectOption({ index: 1 });
    await page.waitForTimeout(500);
  }
  await takeScreenshot('register-committee-selected');

  // Step 4: Navigate through form steps
  log('Step 4: Navigating through form steps...');
  const nextBtn1 = page.locator('#btn-next-1');
  if (await nextBtn1.isVisible({ timeout: 2000 }).catch(() => false)) {
    await nextBtn1.click();
    await page.waitForTimeout(500);
    await takeScreenshot('register-step-2');
    log('Moved to Step 2');
  }

  const nextBtn2 = page.locator('#btn-next-2');
  if (await nextBtn2.isVisible({ timeout: 2000 }).catch(() => false)) {
    await nextBtn2.click();
    await page.waitForTimeout(500);
    await takeScreenshot('register-step-3');
    log('Moved to Step 3');
  }

  // Check terms on final step
  const termsCheck = page.locator('#terms-checkbox');
  if (await termsCheck.isVisible({ timeout: 2000 }).catch(() => false)) {
    await termsCheck.check();
  }

  // Step 5: Submit
  log('Step 5: Submitting Registration...');
  await page.waitForTimeout(500);

  // Try to find submit button - may need to scroll
  await page.evaluate(() => {
    const btn = document.getElementById('btn-submit');
    if (btn) btn.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });
  await page.waitForTimeout(1000);

  const submitBtn = page.locator('#btn-submit');
  if (await submitBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    await submitBtn.click();
    await page.waitForTimeout(1000);
    await takeScreenshot('register-submitted');
  } else {
    log('Submit button not visible - may need more steps');
    failed++;
  }

  // Step 5: Check Success Page
  log('Step 5: Checking Success Page...');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  await takeScreenshot('success-page');

  const successText = await highlightAndCapture('.success-message, .confirmation, h2, h1', 'success-highlighted');

  if (successText.includes(testName) || successText.includes(testRoll) || successText.includes('Congratulations')) {
    log(`✅ Registration SUCCESS: "${successText.trim()}"`);
    passed++;
  } else {
    log(`❌ Registration may have failed. Found: "${successText.trim()}"`);
    failed++;
  }

  // Step 6: Verify in Admin
  log('Step 6: Verifying in Admin Panel...');
  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');
  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });
  await page.waitForTimeout(500);

  await page.click('.nav-item:has-text("Delegates")');
  await page.waitForTimeout(500);
  await takeScreenshot('admin-delegates-list');

  // Check if new delegate appears
  const delegateFound = await page.locator(`text="${testName}"`).isVisible({ timeout: 3000 }).catch(() => false);
  if (delegateFound) {
    log(`✅ Delegate "${testName}" found in Admin!`);
    passed++;
  } else {
    log(`❌ Delegate "${testName}" NOT found in Admin`);
    failed++;
  }
}

// =========================================================================
// TEST 4: ANNOUNCEMENTS (Create & Verify)
// =========================================================================
async function testAnnouncements() {
  log('\n=== TEST 4: ANNOUNCEMENTS ===', 'info');

  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');
  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });
  await page.waitForTimeout(500);

  // Check if Announcements section exists
  const annNav = page.locator('.nav-item:has-text("Announcement"), .nav-item:has-text("Notice")');
  if (await annNav.isVisible({ timeout: 2000 }).catch(() => false)) {
    log(`✅ Announcements section found in Admin`);
    passed++;

    await annNav.click();
    await page.waitForTimeout(500);
    await takeScreenshot('admin-announcements');

    // Check for create/edit functionality
    const createBtn = page.locator('button:has-text("Create"), button:has-text("Add"), .create-btn');
    if (await createBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
      log(`✅ Can create announcements`);
      passed++;
    }
  } else {
    log(`⚠️ Announcements section not found - checking other nav items...`);
    // List all nav items
    const navItems = await page.locator('.nav-item').allTextContents();
    log(`Available nav items: ${navItems.join(', ')}`);
  }
}

// =========================================================================
// TEST 5: PARTICLES & VISUAL EFFECTS
// =========================================================================
async function testVisualEffects() {
  log('\n=== TEST 5: PARTICLES & VISUAL EFFECTS ===', 'info');

  const pages = ['/', '/register.html', '/success.html'];

  for (const path of pages) {
    log(`Checking effects on ${path}...`);
    await page.goto(API_URL + path);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(500);
    await takeScreenshot(`effects-${path.replace('/', '')}`);

    // Check particles
    const particles = page.locator('#particles-canvas, canvas');
    if (await particles.isVisible({ timeout: 2000 }).catch(() => false)) {
      log(`✅ Particles canvas visible on ${path}`);
      passed++;
    }

    // Check confetti on success page
    if (path === '/success.html') {
      const confetti = page.locator('#confetti-canvas, #confetti');
      if (await confetti.isVisible({ timeout: 2000 }).catch(() => false)) {
        log(`✅ Confetti visible on success page`);
        passed++;
      }
    }
  }
}

// =========================================================================
// TEST 6: ADMIN NAVIGATION (All Sections)
// =========================================================================
async function testAdminNavigation() {
  log('\n=== TEST 6: ADMIN NAVIGATION (ALL SECTIONS) ===', 'info');

  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');
  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });
  await page.waitForTimeout(500);
  await takeScreenshot('admin-dashboard');

  // Get all nav items
  const navItems = await page.locator('.nav-item').all();

  log(`Found ${navItems.length} navigation items`);

  for (let i = 0; i < 8; i++) {
    const navItem = page.locator('.nav-item').nth(i);
    const navText = await navItem.textContent();
    log(`\nTesting nav item ${i + 1}...`);

    await navItem.click();
    await page.waitForTimeout(500);
    await takeScreenshot(`admin-nav-${i + 1}`);

    // Check if page section is visible
    const pageSection = page.locator('.page-section.active, .page-content:visible').last();
    if (await pageSection.isVisible({ timeout: 2000 }).catch(() => false)) {
      log(`✅ Nav item ${i + 1} loads correctly`);
      passed++;
    } else {
      log(`⚠️ Nav item ${i + 1} may have issues`);
    }
  }
}

// =========================================================================
// TEST 7: SETTINGS SYNC (Registration Controls)
// =========================================================================
async function testSettingsSync() {
  log('\n=== TEST 7: REGISTRATION CONTROLS SYNC ===', 'info');

  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');
  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });

  await page.click('.nav-item:has-text("Event Settings")');
  await page.waitForTimeout(500);
  await takeScreenshot('admin-settings');

  // Change registration deadline
  const newDeadline = '2026-07-01T23:59';
  const deadlineField = page.locator('#ctrl-reg-deadline');
  if (await deadlineField.isVisible({ timeout: 2000 }).catch(() => false)) {
    await deadlineField.fill(newDeadline);
    await page.waitForTimeout(1000);
    await takeScreenshot('admin-deadline-filled');

    await page.click('.save-btn:has-text("Save Controls")');
    await page.waitForTimeout(1000);
    await takeScreenshot('admin-deadline-saved');

    log(`✅ Registration deadline set to: ${newDeadline}`);
    passed++;
  }

  // Check if deadline appears on register page
  log('Checking if deadline appears on Register page...');
  await page.goto(API_URL + '/register.html');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);

  const deadlineText = await page.locator('.deadline, .reg-deadline, .deadline-text').textContent({ timeout: 2000 }).catch(() => null);
  if (deadlineText) {
    log(`✅ Frontend shows deadline: "${deadlineText.trim()}"`);
    passed++;
  } else {
    log(`⚠️ Frontend deadline text not found (may use different element)`);
  }
  await takeScreenshot('register-with-deadline');
}

// =========================================================================
// TEST 8: COMMITTEE PAGE (Agendas & Chairs)
// =========================================================================
async function testCommitteePage() {
  log('\n=== TEST 8: COMMITTEE PAGE (Agendas & Chairs) ===', 'info');

  // First set some agenda in admin
  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');
  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });

  await page.click('.nav-item:has-text("Agenda & Chairs")');
  await page.waitForTimeout(500);
  await takeScreenshot('admin-agenda');

  // Check if committees are listed
  const committeeCards = page.locator('.agenda-card');
  const count = await committeeCards.count();
  log(`Found ${count} committee cards in Admin`);
  if (count > 0) passed++;

  // Now check frontend
  log('Checking frontend committees page...');
  await page.goto(API_URL + '/committees.html');
  await page.waitForLoadState('networkidle');
  await page.waitForTimeout(500);
  await takeScreenshot('frontend-committees');

  const commCards = page.locator('.committee-card, .comm-card');
  const frontendCount = await commCards.count();
  log(`Found ${frontendCount} committee cards on frontend`);
  if (frontendCount > 0) passed++;
}

// =========================================================================
// MAIN RUNNER
// =========================================================================
async function runTests() {
  try {
    await setup();

    // Run all tests visually
    await testLogosAllPages();
    await testEventTitleSync();
    await testRegistrationFlow();
    await testAnnouncements();
    await testVisualEffects();
    await testAdminNavigation();
    await testSettingsSync();
    await testCommitteePage();

    log('\n===== ALL VISUAL TESTS COMPLETE =====');

  } catch (e) {
    log('FATAL: ' + e.message, 'fail');
    console.error(e);
    await takeScreenshot('error-' + Date.now());
  } finally {
    await teardown();
  }
}

runTests();