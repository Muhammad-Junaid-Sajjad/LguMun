/**
 * Phase 2: Duplicate Registration Test
 * Verifies that duplicate Email and CNIC are blocked by backend
 */

const { chromium } = require('playwright');

async function runDuplicateTest() {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  const uniqueId = Date.now();
  const testData = {
    name: 'Duplicate Test User',
    email: `dup${uniqueId}@test.com`,
    cnic: `DUP-${uniqueId}`,
    phone: '03001112233',
    institution: 'Duplicate University'
  };

  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
  console.log('🧪 PHASE 2: DUPLICATE REGISTRATION TEST');
  console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n');

  try {
    // 1. Register the FIRST time
    console.log('📍 1. Performing initial registration...');
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
    console.log('   ✅ First registration successful');

    // 2. Attempt duplicate EMAIL
    console.log('\n📍 2. Attempting duplicate EMAIL...');
    await page.goto('http://localhost:8000/register.html');
    await page.fill('#full_name', 'Another User');
    await page.fill('#student_id_cnic', `CNIC-${uniqueId}-2`); // Unique CNIC
    await page.fill('#email', testData.email); // DUPLICATE EMAIL
    await page.fill('#phone', '03009998877');
    await page.fill('#institution', 'Another Uni');
    await page.click('#btn-next-1');
    await page.waitForTimeout(1000);
    await page.selectOption('#committee_id', { index: 1 });
    await page.click('#btn-next-2');
    await page.waitForTimeout(1000);
    await page.click('#terms-checkbox');
    await page.click('#btn-submit');

    // Wait for error message
    await page.waitForTimeout(3000);
    const bodyText = await page.textContent('body');
    const hasError = bodyText.toLowerCase().includes('already registered') ||
                     bodyText.toLowerCase().includes('exists') ||
                     await page.isVisible('.form-error:not(.hidden)');

    console.log(`   Result: ${hasError ? '✅ BLOCKED (Correct)' : '❌ ALLOWED (Bug!)'}`);

    // 3. Attempt duplicate CNIC
    console.log('\n📍 3. Attempting duplicate CNIC...');
    await page.goto('http://localhost:8000/register.html');
    await page.fill('#full_name', 'Third User');
    await page.fill('#student_id_cnic', testData.cnic); // DUPLICATE CNIC
    await page.fill('#email', `third${uniqueId}@test.com`); // Unique Email
    await page.fill('#phone', '03005556677');
    await page.fill('#institution', 'Third Uni');
    await page.click('#btn-next-1');
    await page.waitForTimeout(1000);
    await page.selectOption('#committee_id', { index: 1 });
    await page.click('#btn-next-2');
    await page.waitForTimeout(1000);
    await page.click('#terms-checkbox');
    await page.click('#btn-submit');

    await page.waitForTimeout(3000);
    const bodyText2 = await page.textContent('body');
    const hasError2 = bodyText2.toLowerCase().includes('already registered') ||
                      bodyText2.toLowerCase().includes('exists') ||
                      await page.isVisible('.form-error:not(.hidden)');

    console.log(`   Result: ${hasError2 ? '✅ BLOCKED (Correct)' : '❌ ALLOWED (Bug!)'}`);

    await page.screenshot({ path: 'test-results/phase2-duplicate-test.png', fullPage: true });

  } catch (error) {
    console.error('❌ TEST ERROR:', error.message);
  } finally {
    await browser.close();
  }
}

runDuplicateTest();