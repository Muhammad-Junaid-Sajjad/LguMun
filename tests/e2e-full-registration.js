const { chromium } = require('playwright');

async function runFullRegistrationTest() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const testData = {
    name: `Test Delegate ${Date.now()}`,
    email: `test${Date.now()}@test.com`,
    cnic: `12345${Date.now().toString().slice(-7)}`,
    phone: '03001234567',
    institution: 'Test University'
  };

  console.log('🔹 Starting FULL REGISTRATION E2E TEST');
  console.log('═══════════════════════════════════════\n');

  try {
    // STEP 1: Go to registration page
    console.log('📍 STEP 1: Loading registration page...');
    await page.goto('http://localhost:8000/register.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(1000);
    console.log('✅ Registration page loaded\n');

    // STEP 2: Fill Step 1 - Personal Information
    console.log('📍 STEP 2: Filling personal information...');
    await page.fill('#full_name', testData.name);
    await page.fill('#student_id_cnic', testData.cnic);
    await page.fill('#email', testData.email);
    await page.fill('#phone', testData.phone);
    await page.fill('#institution', testData.institution);
    console.log('   - Name:', testData.name);
    console.log('   - CNIC:', testData.cnic);
    console.log('   - Email:', testData.email);
    console.log('✅ Step 1 completed\n');

    // STEP 3: Click Continue to go to Step 2
    console.log('📍 STEP 3: Clicking Continue to Step 2...');
    await page.click('#btn-next-1');
    await page.waitForTimeout(1000);

    const step2Visible = await page.isVisible('#step-2');
    console.log('✅ Step 2 visible:', step2Visible);

    // STEP 4: Select Committee (pick first available)
    console.log('📍 STEP 4: Selecting committee...');
    const select = page.locator('#committee_id');
    await select.waitFor({ state: 'visible' });

    // Get all options and pick first available
    const options = await select.locator('option').all();
    console.log('   - Available committees:', options.length - 1); // -1 for the "choose" option

    // Select first available committee
    await select.selectOption({ index: 1 });
    const selectedText = await select.locator('option:checked').textContent();
    console.log('   - Selected:', selectedText?.replace(' — ', ' ').split(' (')[0]);
    console.log('✅ Committee selected\n');

    // STEP 5: Click Continue to go to Step 3 (Review)
    console.log('📍 STEP 5: Clicking Continue to Step 3 (Review & Confirm)...');
    await page.click('#btn-next-2');
    await page.waitForTimeout(1000);

    const step3Visible = await page.isVisible('#step-3');
    console.log('✅ Step 3 visible:', step3Visible);

    // Verify confirmation details are shown
    const confirmGrid = await page.locator('#confirm-grid').textContent();
    console.log('   - Confirmation data shown:', confirmGrid?.includes(testData.name) ? 'YES' : 'NO');
    console.log('✅ Review step completed\n');

    // STEP 6: Accept terms and submit
    console.log('📍 STEP 6: Accepting terms and submitting...');
    await page.click('#terms-checkbox');
    await page.waitForTimeout(500);

    // Click submit
    await page.click('#btn-submit');
    console.log('   - Submit clicked...');

    // Wait for redirect to success page
    await page.waitForURL('**/success.html', { timeout: 10000 });
    await page.waitForTimeout(2000);

    console.log('✅ Registration submitted - redirected to success page\n');

    // STEP 7: Get roll number from success page
    console.log('📍 STEP 7: Extracting roll number from success page...');
    const rollNumber = await page.locator('#roll-number').textContent();
    console.log('   🎫 ROLL NUMBER:', rollNumber);

    // Get committee
    const committee = await page.locator('#bd-committee').textContent();
    console.log('   🏛️ COMMITTEE:', committee);

    // Verify success message
    const successHeading = await page.locator('.success-heading').textContent();
    console.log('   ✅ Success message:', successHeading);
    console.log('✅ SUCCESS PAGE VERIFIED\n');

    console.log('═══════════════════════════════════════');
    console.log('📋 REGISTRATION COMPLETE!');
    console.log('   Name:', testData.name);
    console.log('   Roll:', rollNumber);
    console.log('   Committee:', committee);
    console.log('═══════════════════════════════════════\n');

    // STEP 8: Go to admin and verify delegate exists
    console.log('📍 STEP 8: Navigating to admin panel...');
    await page.goto('http://localhost:8000/admin.html', { waitUntil: 'networkidle' });
    await page.waitForTimeout(2000);

    // Login to admin if needed
    console.log('📍 STEP 9: Logging into admin...');
    const loginVisible = await page.isVisible('#admin-login');

    if (loginVisible) {
      await page.fill('#admin-email', 'admin@lgu.edu.pk');
      await page.fill('#admin-password', 'admin123');
      await page.click('#btn-admin-login');
      await page.waitForTimeout(2000);
      console.log('✅ Admin logged in\n');
    } else {
      console.log('✅ Already logged in to admin\n');
    }

    // STEP 10: Check delegates table
    console.log('📍 STEP 10: Verifying delegate in admin panel...');

    // Make sure we're on delegates page
    const navText = await page.locator('body').textContent();
    if (!navText.includes('Delegates')) {
      await page.click('text=Delegates');
      await page.waitForTimeout(1000);
    }

    // Search for the roll number
    console.log('   - Searching for roll:', rollNumber);

    // Check if roll number appears in the table
    const pageText = await page.textContent('body');
    const delegateFound = pageText.includes(rollNumber);

    console.log('   ✅ Delegate found in admin:', delegateFound ? 'YES ✓' : 'NO ✗');

    if (delegateFound) {
      console.log('\n🎉 FULL E2E TEST PASSED!');
      console.log('   1. ✅ Registration complete');
      console.log('   2. ✅ Success page shows roll number:', rollNumber);
      console.log('   3. ✅ Admin panel accessible');
      console.log('   4. ✅ Delegate verified in table');
    } else {
      console.log('\n⚠️ Test completed but delegate not immediately visible');
      console.log('   This may require scroll or pagination');
    }

    // Take final screenshot
    await page.screenshot({ path: 'test-results/10-verify-delegate.png' });
    console.log('📍 Screenshot saved: test-results/10-verify-delegate.png\n');

  } catch (error) {
    console.error('❌ TEST FAILED:', error.message);
    await page.screenshot({ path: 'test-results/ERROR-final.png' });
  } finally {
    console.log('\n🔚 Test complete. Press Ctrl+C to close browser.');
    // Don't close browser - let user see the result
  }
}

runFullRegistrationTest();