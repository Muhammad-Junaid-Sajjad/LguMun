// E2E Test - Admin Login Scenario with Debugging
// Run with: node test-admin-login.js

const { chromium } = require('playwright');

async function testAdminLogin() {
  console.log('🚀 Starting E2E Admin Login Debugging Test...\n');

  const browser = await chromium.launch({ headless: true }); // Run headless for the agent
  const page = await browser.newPage();

  // Listen for console messages
  page.on('console', msg => {
    const text = msg.text();
    const type = msg.type();
    console.log(`[BROWSER CONSOLE ${type.toUpperCase()}] ${text}`);
  });

  // Listen for page errors
  page.on('pageerror', err => {
    console.log('[BROWSER PAGE ERROR]', err.message);
  });

  // Listen for failed requests
  page.on('requestfailed', request => {
    console.log('[BROWSER REQUEST FAILED]', request.url(), request.failure().errorText);
  });

  const API_KEY = 'lgumun2026_admin_secure_key_x9y2z';
  const ADMIN_URL = 'http://localhost:8000/admin.html';

  try {
    // 1. Navigate to admin page
    console.log('📍 Step 1: Navigating to admin page...');
    await page.goto(ADMIN_URL, { waitUntil: 'networkidle' });
    console.log('   ✅ Page loaded: ' + page.url());

    // 2. Fill Administrator ID
    console.log('📍 Step 2: Entering Administrator ID...');
    await page.fill('#login-user', 'admin');

    // 3. Fill Access Code
    console.log('📍 Step 3: Entering Access Code...');
    await page.fill('#login-pass', API_KEY);

    // 4. Click authenticate button
    console.log('📍 Step 4: Clicking Authenticate button...');
    await page.click('.login-btn');

    // 5. Wait for response and potential transitions
    console.log('📍 Step 5: Waiting for response/transition (6s)...');
    await page.waitForTimeout(6000);

    // 6. Final State Check
    console.log('\n📊 Final State Analysis:');

    const isLoginVisible = await page.isVisible('#login-screen');
    const isAppVisible = await page.isVisible('#app');
    const loginError = await page.isVisible('#login-err.show');

    console.log(`   Login Screen Visible: ${isLoginVisible}`);
    console.log(`   App Container Visible: ${isAppVisible}`);
    console.log(`   Error Message Shown: ${loginError}`);

    if (loginError) {
      const errorText = await page.textContent('#login-err.show');
      console.log(`   ❌ ERROR SHOWN: ${errorText}`);
    }

    if (isAppVisible) {
      console.log('   ✅ SUCCESS! App is visible.');
    } else {
      console.log('   ❌ FAILED! App is NOT visible.');
    }

    // 7. Take screenshot
    console.log('\n📸 Taking final screenshot...');
    await page.screenshot({ path: 'admin-login-debug.png', fullPage: true });
    console.log('   Saved to: admin-login-debug.png');

  } catch (error) {
    console.log('\n❌ SCRIPT ERROR: ' + error.message);
  } finally {
    await browser.close();
    console.log('\n🔚 Debugging test complete.');
  }
}

testAdminLogin();
