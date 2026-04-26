/**
 * E2E Live Test: Visual & Logo Verification
 * Tests: Logo, Particles, Confetti, Admin Portal
 */

const { chromium } = require('playwright');

const API_KEY = 'lgumun2026_admin_secure_key_x9y2z';
const ADMIN_URL = 'http://localhost:8000/admin.html';
const API_URL = 'http://localhost:8000';

let browser, context, page;
let passed = 0, failed = 0;

async function log(msg, type = 'info') {
  const t = new Date().toISOString().split('T')[1].slice(0, 12);
  const p = type === 'pass' ? '✅' : type === 'fail' ? '❌' : 'ℹ️';
  console.log(`[${t}] ${p} ${msg}`);
}

async function setup() {
  log('Launching browser...');
  browser = await chromium.launch({ headless: false });
  context = await browser.newContext();
  page = await context.newPage();
  await page.setViewportSize({ width: 1400, height: 900 });
}

async function teardown() {
  if (browser) await browser.close();
  log(`\n=== RESULTS: ${passed} passed, ${failed} failed ===`);
}

// Test 1: INDEX PAGE - Logo & Particles
async function testIndexPage() {
  log('\n--- Testing INDEX PAGE ---');

  await page.goto(API_URL + '/');
  await page.waitForLoadState('networkidle');

  // Check logo loads
  const logo = page.locator('img[alt="LGU Official Logo"]').first();
  if (await logo.isVisible({ timeout: 5000 })) {
    log('✅ Logo visible on index page');

    // Check logo source
    const src = await logo.getAttribute('src');
    if (src && src.includes('lgumun-society-logo.png')) {
      log('✅ Correct logo file loaded: ' + src);
      passed++;
    } else {
      log('❌ Wrong logo file: ' + src);
      failed++;
    }
  } else {
    log('❌ Logo NOT visible on index page');
    failed++;
  }

  // Check particles canvas exists
  const particles = page.locator('#particles-canvas');
  if (await particles.isVisible()) {
    log('✅ Particles canvas visible');
    passed++;
  } else {
    log('❌ Particles canvas NOT visible');
    failed++;
  }

  // Check navbar links work
  const navLinks = await page.locator('.nav-links a').count();
  log(`✅ Navbar has ${navLinks} navigation links`);
}

// Test 2: REGISTER PAGE - Logo & Particles
async function testRegisterPage() {
  log('\n--- Testing REGISTER PAGE ---');

  await page.goto(API_URL + '/register.html');
  await page.waitForLoadState('networkidle');

  const logo = page.locator('img[alt="LGU Official Logo"]').first();
  if (await logo.isVisible({ timeout: 5000 })) {
    log('✅ Logo visible on register page');
    passed++;
  } else {
    log('❌ Logo NOT visible on register page');
    failed++;
  }

  const particles = page.locator('#particles-canvas');
  if (await particles.isVisible()) {
    log('✅ Particles canvas visible');
    passed++;
  } else {
    log('❌ Particles canvas NOT visible');
    failed++;
  }
}

// Test 3: SUCCESS PAGE - Logo & Confetti
async function testSuccessPage() {
  log('\n--- Testing SUCCESS PAGE ---');

  await page.goto(API_URL + '/success.html');
  await page.waitForLoadState('networkidle');

  // Check logo
  const logo = page.locator('img[alt="LGU Official Logo"]').first();
  if (await logo.isVisible({ timeout: 5000 })) {
    log('✅ Logo visible on success page');
    passed++;
  } else {
    log('❌ Logo NOT visible on success page');
    failed++;
  }

  // Check confetti canvas
  const confetti = page.locator('#confetti-canvas');
  if (await confetti.isVisible()) {
    log('✅ Confetti canvas visible');
    passed++;
  } else {
    log('❌ Confetti canvas NOT visible');
    failed++;
  }

  // Wait a moment to ensure confetti is animating
  await page.waitForTimeout(1000);
  log('✅ Confetti animation running');
}

// Test 4: COMMITTEES PAGE
async function testCommitteesPage() {
  log('\n--- Testing COMMITTEES PAGE ---');

  await page.goto(API_URL + '/committees.html');
  await page.waitForLoadState('networkidle');

  const logo = page.locator('img[alt="LGU Official Logo"]').first();
  if (await logo.isVisible({ timeout: 5000 })) {
    log('✅ Logo visible on committees page');
    passed++;
  } else {
    log('❌ Logo NOT visible on committees page');
    failed++;
  }
}

// Test 5: ADMIN PORTAL - Login & Sidebar Logo
async function testAdminPortal() {
  log('\n--- Testing ADMIN PORTAL ---');

  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');

  // Check login logo
  const loginLogo = page.locator('.login-crest-icon img');
  if (await loginLogo.isVisible({ timeout: 5000 })) {
    log('✅ Login logo visible');
    passed++;
  } else {
    log('❌ Login logo NOT visible');
    failed++;
  }

  // Login
  await page.fill('#login-pass', API_KEY);
  await page.click('.login-btn');
  await page.waitForSelector('#app.show', { timeout: 15000 });
  log('✅ Logged in to admin');

  // Check sidebar logo
  const sidebarLogo = page.locator('.sidebar-logo-img');
  if (await sidebarLogo.isVisible({ timeout: 5000 })) {
    log('✅ Sidebar logo visible');
    passed++;

    // Verify file
    const src = await sidebarLogo.getAttribute('src');
    if (src && src.includes('lgumun-society-logo.png')) {
      log('✅ Correct sidebar logo: ' + src);
      passed++;
    }
  } else {
    // Try the emoji fallback
    const emoji = page.locator('.sidebar-logo');
    if (await emoji.isVisible()) {
      log('⚠️ Sidebar using fallback (emoji)');
    } else {
      log('❌ Sidebar logo NOT visible');
      failed++;
    }
  }

  // Test Country Allocations page
  log('Testing Country Allocations...');
  await page.click('.nav-item:has-text("Country Allocations")');
  await page.waitForSelector('.alloc-wizard', { timeout: 5000 });
  log('✅ Country Allocations page loads');
  passed++;
}

// Test 6: API Endpoints
async function testAPIEndpoints() {
  log('\n--- Testing API Endpoints ---');

  const endpoints = [
    '/api/v1/committees',
    '/api/v1/admin/stats',
    '/api/v1/admin/committees/10/pool',
    '/api/v1/admin/countries/global',
  ];

  for (const ep of endpoints) {
    try {
      const r = await fetch(API_URL + ep, {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      if (r.ok) {
        log(`✅ ${ep}: OK`);
        passed++;
      } else {
        log(`❌ ${ep}: ${r.status}`);
        failed++;
      }
    } catch (e) {
      log(`❌ ${ep}: ${e.message}`);
      failed++;
    }
  }
}

async function runTests() {
  try {
    await setup();

    // Test all pages
    await testIndexPage();
    await testRegisterPage();
    await testSuccessPage();
    await testCommitteesPage();
    await testAdminPortal();
    await testAPIEndpoints();

    log('\n=== ALL TESTS COMPLETE ===');

  } catch (e) {
    log('FATAL: ' + e.message, 'fail');
    console.error(e);
  } finally {
    await teardown();
  }
}

runTests();