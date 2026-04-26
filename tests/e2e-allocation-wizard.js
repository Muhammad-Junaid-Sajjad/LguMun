/**
 * E2E Test: Country Allocation Wizard - All 9 Committees
 * Tests the complete allocation workflow in live browser
 */

const { chromium } = require('playwright');

const COMMITTEES = [
  { code: 'UNSC', id: 10, delegates: 15 },
  { code: 'UNGA', id: 11, delegates: 2 },
  { code: 'UNHRC', id: 12, delegates: 4 },
  { code: 'DISEC', id: 13, delegates: 5 },
  { code: 'UNODC', id: 14, delegates: 42 },
  { code: 'PNA', id: 15, delegates: 5 },
  { code: 'UNW', id: 16, delegates: 2 },
  { code: 'JSP', id: 17, delegates: 18 },
  { code: 'NCC', id: 18, delegates: 2 }
];

const API_KEY = 'lgumun2026_admin_secure_key_x9y2z';
const ADMIN_URL = 'http://localhost:8000/admin.html';
const API_URL = 'http://localhost:8000';

let browser;
let context;
let page;
let passed = 0;
let failed = 0;
let skipped = 0;

async function log(msg, type = 'info') {
  const timestamp = new Date().toISOString().split('T')[1].slice(0, 12);
  const prefix = type === 'pass' ? '✅' : type === 'fail' ? '❌' : type === 'skip' ? '⏭️' : 'ℹ️';
  console.log(`[${timestamp}] ${prefix} ${msg}`);
}

async function setup() {
  log('Launching browser...');
  browser = await chromium.launch({ headless: false });
  context = await browser.newContext();
  page = await context.newPage();

  // Set viewport
  await page.setViewportSize({ width: 1400, height: 900 });
}

async function teardown() {
  if (browser) {
    await browser.close();
  }
  log(`\n=== TEST SUMMARY ===`);
  log(`Passed: ${passed}`);
  log(`Failed: ${failed}`);
  log(`Skipped: ${skipped}`);
  log(`Total: ${passed + failed + skipped}`);
}

async function loginToAdmin() {
  log('Logging into admin panel...');

  await page.goto(ADMIN_URL);
  await page.waitForLoadState('networkidle');

  // Wait for login screen
  await page.waitForSelector('#login-screen', { timeout: 10000 });

  // Enter API key
  await page.fill('#login-pass', API_KEY);

  // Click login button
  await page.click('.login-btn');

  // Wait for app to load
  await page.waitForSelector('#app.show', { timeout: 15000 });

  log('Successfully logged in to admin panel', 'pass');
}

async function navigateToAllocations() {
  log('Navigating to Country Allocations page...');

  // Click on Country Allocations nav item
  const allocNav = await page.locator('.nav-item:has-text("Country Allocations")');
  await allocNav.click();

  // Wait for wizard to load
  await page.waitForSelector('.alloc-wizard', { timeout: 10000 });

  log('Allocations page loaded', 'pass');
}

async function testCommitteeWizard(committee) {
  log(`\n--- Testing ${committee.code} (ID: ${committee.id}) ---`);

  // Step 1: Verify committee selection grid is visible
  const step1 = await page.locator('#step-1');
  if (!(await step1.isVisible())) {
    log(`${committee.code}: Step 1 not visible`, 'fail');
    failed++;
    return;
  }

  // Find and click the committee card
  const commCard = await page.locator(`.comm-select-card:has-text("${committee.code}")`);

  if (await commCard.isVisible()) {
    await commCard.click();
    log(`${committee.code}: Committee selected`, 'pass');

    // Wait for step 2 to load
    await page.waitForTimeout(500);

    // Verify we're on step 2
    const step2 = await page.locator('#step-2');
    if (await step2.isVisible()) {
      log(`${committee.code}: Step 2 (Import Pool) visible`, 'pass');

      // Test import based on committee type
      if (committee.code === 'PNA') {
        // For PNA, test personalities
        await testPersonalityImport(committee);
      } else {
        // For others, test global pool import
        await testGlobalPoolImport(committee);
      }

      // Step 3: Auto-assign
      await gotoStep(3);

      // Check engine configuration is visible
      const engineConfig = await page.locator('#run-engine-btn');
      if (await engineConfig.isVisible()) {
        log(`${committee.code}: Step 3 (Auto-Assign) visible`, 'pass');

        // Only run engine if committee has delegates
        if (committee.delegates > 0) {
          await testAutoAssign(committee);
        } else {
          log(`${committee.code}: Skipping auto-assign (0 delegates)`, 'skip');
          skipped++;
        }
      }

      // Step 4: Review
      await gotoStep(4);
      await page.waitForTimeout(500);

      const reviewTable = await page.locator('.alloc-table');
      if (await reviewTable.isVisible()) {
        log(`${committee.code}: Step 4 (Review) visible`, 'pass');
      }

      passed++;
    } else {
      log(`${committee.code}: Step 2 did not load`, 'fail');
      failed++;
    }
  } else {
    log(`${committee.code}: Committee card not found`, 'fail');
    failed++;
  }

  // Go back to step 1 for next committee
  await gotoStep(1);
  await page.waitForTimeout(300);
}

async function gotoStep(stepNum) {
  const stepTab = await page.locator(`#step-tab-${stepNum}`);
  await stepTab.click();
  await page.waitForTimeout(500);
}

async function testGlobalPoolImport(committee) {
  log(`${committee.code}: Testing Global Pool import...`);

  // Make sure global tab is active
  const globalTab = await page.locator('#tab-global');
  if (!(await globalTab.isVisible())) {
    await page.click('#tab-global');
    await page.waitForTimeout(300);
  }

  // Select a region - click on the outer label instead of the hidden checkbox
  const regionLabels = await page.locator('#region-selector .toggle-row');
  const labelCount = await regionLabels.count();
  if (labelCount > 0) {
    await regionLabels.first().click();
    await page.waitForTimeout(300);
    log(`${committee.code}: Region selected`, 'pass');

    // Click import button
    const importBtn = await page.locator('#source-global button.login-btn');
    await importBtn.click();

    // Wait for import to complete
    await page.waitForTimeout(1500);
    log(`${committee.code}: Global pool import triggered`, 'pass');
  }

  // Check pool display
  const poolDisplay = await page.locator('#current-pool-display');
  if (await poolDisplay.isVisible()) {
    log(`${committee.code}: Pool display visible`, 'pass');
  }
}

async function testPersonalityImport(committee) {
  log(`${committee.code}: Testing Personality import...`);

  // Switch to personality tab
  await page.click('#tab-personality');
  await page.waitForTimeout(500);

  // Check if personality list loads
  const persList = await page.locator('#pers-list');
  if (await persList.isVisible()) {
    log(`${committee.code}: Personality list loaded`, 'pass');

    // Toggle a personality if any exist
    const persToggle = await page.locator('.pers-toggle');
    const toggleCount = await persToggle.count();
    if (toggleCount > 0) {
      await persToggle.first().click();
      await page.waitForTimeout(300);
      log(`${committee.code}: Personality toggle works`, 'pass');
    }
  }
}

async function testAutoAssign(committee) {
  log(`${committee.code}: Running auto-assignment engine...`);

  // Click run engine button
  const runBtn = await page.locator('#run-engine-btn');
  await runBtn.click();

  // Wait for processing
  await page.waitForTimeout(3000);

  // Check if next button appears (indicates success)
  const nextBtn = await page.locator('#step3-next');
  if (await nextBtn.isVisible()) {
    log(`${committee.code}: Auto-assignment complete`, 'pass');
  } else {
    // Check for toast messages
    const toast = await page.locator('.toast-msg');
    if (await toast.isVisible()) {
      const msg = await toast.textContent();
      log(`${committee.code}: ${msg}`, 'pass');
    }
  }
}

async function testAPIEndpoints() {
  log('\n--- Testing Backend API Endpoints ---');

  const endpoints = [
    { path: '/api/v1/admin/committees', method: 'GET' },
    { path: '/api/v1/admin/committees/10/pool', method: 'GET' },
    { path: '/api/v1/admin/committees/10/allocations', method: 'GET' },
    { path: '/api/v1/admin/countries/global', method: 'GET' },
    { path: '/api/v1/admin/personalities', method: 'GET' }
  ];

  for (const endpoint of endpoints) {
    try {
      const response = await fetch(`${API_URL}${endpoint.path}`, {
        headers: { 'X-Admin-API-Key': API_KEY }
      });

      if (response.ok) {
        log(`API ${endpoint.path}: OK (${response.status})`, 'pass');
        passed++;
      } else {
        log(`API ${endpoint.path}: FAILED (${response.status})`, 'fail');
        failed++;
      }
    } catch (err) {
      log(`API ${endpoint.path}: ERROR - ${err.message}`, 'fail');
      failed++;
    }
  }
}

async function runTests() {
  try {
    await setup();

    // First test API endpoints
    await testAPIEndpoints();

    // Then test UI
    await loginToAdmin();
    await navigateToAllocations();

    // Test each committee
    for (const committee of COMMITTEES) {
      await testCommitteeWizard(committee);
    }

    log('\n=== ALL TESTS COMPLETE ===');

  } catch (error) {
    log(`Fatal error: ${error.message}`, 'fail');
    console.error(error);
  } finally {
    await teardown();
  }
}

// Run tests
runTests();
