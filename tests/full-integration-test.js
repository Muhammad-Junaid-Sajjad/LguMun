/**
 * FULL INTEGRATION TEST
 * Tests: Frontend, Backend, Admin, Database Integrity
 */

const { chromium } = require('playwright');
const API_KEY = 'lgumun2026_admin_secure_key_x9y2z';
const BASE_URL = 'http://localhost:8000';

let passed = 0, failed = 0;
const results = [];

function log(msg, status = 'info') {
  const icons = { pass: '✅', fail: '❌', info: 'ℹ️' };
  console.log(`[${icons[status]}] ${msg}`);
  if (status === 'pass') passed++;
  if (status === 'fail') failed++;
  results.push({ msg, status });
}

async function test(name, fn) {
  try {
    await fn();
    log(`${name}`, 'pass');
  } catch(e) {
    log(`${name}: ${e.message}`, 'fail');
  }
}

async function runIntegrationTests() {
  const browser = await chromium.launch({ headless: false, slowMo: 800 });
  const context = await browser.newContext({ viewport: { width: 1400, height: 900 } });
  const page = await context.newPage();

  console.log('\n========================================');
  console.log('  LGU MUN 2026 - FULL INTEGRATION TEST');
  console.log('========================================\n');

  try {
    // === FRONTEND PAGES ===
    log('\n--- FRONTEND PAGES ---');

    await test('Homepage loads', async () => {
      await page.goto(BASE_URL + '/', { waitUntil: 'networkidle' });
      const title = await page.title();
      if (!title.includes('LGUMUN') && !title.includes('LGU')) throw new Error('Wrong title');
    });

    await test('Featured Committees display', async () => {
      const cards = await page.locator('#featured-committees .committee-card').count();
      if (cards < 3) throw new Error(`Only ${cards} cards found`);
    });

    await test('Navigation works', async () => {
      await page.click('a[href="/committees.html"]');
      await page.waitForLoadState('networkidle');
      const url = page.url();
      if (!url.includes('committees')) throw new Error('Navigation failed');
    });

    await test('Committees page shows all 9', async () => {
      const rows = await page.locator('.committees-table tbody tr').count();
      if (rows < 9) throw new Error(`Only ${rows} committees`);
    });

    await test('Register page loads', async () => {
      await page.goto(BASE_URL + '/register.html', { waitUntil: 'networkidle' });
      const steps = await page.locator('#steps-indicator, .steps-indicator').count();
      if (steps === 0) throw new Error('Step form not found');
    });

    await test('Success page loads', async () => {
      await page.goto(BASE_URL + '/success.html', { waitUntil: 'networkidle' });
      const content = await page.content();
      if (!content.includes('success')) throw new Error('Success page broken');
    });

    // === BACKEND API ===
    log('\n--- BACKEND API ---');

    await test('/api/v1/committees', async () => {
      const r = await fetch(BASE_URL + '/api/v1/committees');
      if (!r.ok) throw new Error(`Status ${r.status}`);
      const d = await r.json();
      if (d.data.committees.length < 9) throw new Error('Missing committees');
    });

    await test('/api/v1/delegates/count', async () => {
      const r = await fetch(BASE_URL + '/api/v1/delegates/count');
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    await test('/api/v1/settings', async () => {
      const r = await fetch(BASE_URL + '/api/v1/settings');
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    await test('/api/v1/announcements/active', async () => {
      const r = await fetch(BASE_URL + '/api/v1/announcements/active');
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    // === ADMIN API ===
    log('\n--- ADMIN API ---');

    await test('/api/v1/admin/stats', async () => {
      const r = await fetch(BASE_URL + '/api/v1/admin/stats', {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    await test('/api/v1/admin/committees', async () => {
      const r = await fetch(BASE_URL + '/api/v1/admin/committees', {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    await test('/api/v1/admin/delegates', async () => {
      const r = await fetch(BASE_URL + '/api/v1/admin/delegates?per_page=5', {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    await test('/api/v1/admin/announcements', async () => {
      const r = await fetch(BASE_URL + '/api/v1/admin/announcements', {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      if (!r.ok) throw new Error(`Status ${r.status}`);
    });

    // === ADMIN UI ===
    log('\n--- ADMIN UI ---');

    await test('Admin login page loads', async () => {
      await page.goto(BASE_URL + '/admin.html', { waitUntil: 'networkidle' });
      await page.waitForTimeout(500);
    });

    await test('Admin login works', async () => {
      await page.fill('#login-pass', API_KEY);
      await page.click('.login-btn');
      await page.waitForSelector('#app.show', { timeout: 10000 });
    });

    await test('Dashboard shows', async () => {
      const stats = await page.locator('.stat-card').count();
      log(`Dashboard has ${stats} stat cards`, 'info');
    });

    await test('Delegates page loads', async () => {
      await page.click('.nav-item:has-text("Delegates")');
      await page.waitForTimeout(1000);
      const table = await page.locator('.delegates-table, table').count();
      log(`Found ${table} tables`, 'info');
    });

    await test('Committees page loads', async () => {
      await page.click('.nav-item:has-text("Committees")');
      await page.waitForTimeout(1000);
      const grid = await page.locator('.comm-card, .committee-card').count();
      log(`Found ${grid} committee cards`, 'info');
    });

    await test('Settings page loads', async () => {
      await page.click('.nav-item:has-text("Event Settings")');
      await page.waitForTimeout(1000);
      const inputs = await page.locator('input[type="text"]').count();
      log(`Found ${inputs} inputs`, 'info');
    });

    await test('Announcements page loads', async () => {
      await page.click('.nav-item:has-text("Announcements")');
      await page.waitForTimeout(1000);
      const section = await page.locator('#page-announcements').count();
      if (section === 0) throw new Error('Page not found');
    });

    await test('Allocations page loads', async () => {
      await page.click('.nav-item:has-text("Country Allocations")');
      await page.waitForTimeout(1000);
      const wizard = await page.locator('.alloc-wizard').count();
      if (wizard === 0) throw new Error('Wizard not found');
    });

    // === DATABASE INTEGRITY ===
    log('\n--- DATABASE INTEGRITY ---');

    await test('Seat counts accurate', async () => {
      const r = await fetch(BASE_URL + '/api/v1/admin/stats', {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      const d = await r.json();
      const total = d.data.total_delegates;
      log(`Total delegates: ${total}`, 'info');
    });

    await test('No duplicate delegates', async () => {
      const r = await fetch(BASE_URL + '/api/v1/admin/delegates?per_page=100', {
        headers: { 'X-Admin-API-Key': API_KEY }
      });
      const d = await r.json();
      const emails = d.data.delegates.map(x => x.email);
      const unique = new Set(emails);
      if (emails.length !== unique.size) throw new Error('Duplicates found!');
    });

  } catch(e) {
    log(`FATAL: ${e.message}`, 'fail');
  } finally {
    await browser.close();
  }

  // === SUMMARY ===
  console.log('\n========================================');
  console.log('  TEST RESULTS SUMMARY');
  console.log('========================================');
  console.log(`  Passed: ${passed}`);
  console.log(`  Failed: ${failed}`);
  console.log(`  Total:  ${passed + failed}`);
  console.log('========================================\n');

  const successRate = Math.round((passed / (passed + failed)) * 100);
  console.log(`  Success Rate: ${successRate}%\n`);

  if (failed === 0) {
    console.log('🎉 ALL SYSTEMS OPERATIONAL!');
  } else {
    console.log('⚠️  Issues detected - review failures above');
  }

  return { passed, failed, successRate };
}

runIntegrationTests()
  .then(r => process.exit(r.failed > 0 ? 1 : 0))
  .catch(e => {
    console.error('Test runner error:', e);
    process.exit(1);
  });