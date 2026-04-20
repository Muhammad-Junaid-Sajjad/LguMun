const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('Testing LGU MUN 2026 Frontend...\n');

  // Test 1: Homepage
  console.log('1. Testing homepage...');
  await page.goto('http://localhost:8000');
  await page.waitForLoadState('networkidle');

  // Check navbar
  const navbar = await page.locator('header');
  if (await navbar.count() > 0) {
    console.log('   ✓ Navbar present');
  } else {
    console.log('   ✗ Navbar missing');
  }

  // Check logo
  const logo = await page.locator('img[alt="LGU MUN"]');
  if (await logo.count() > 0) {
    console.log('   ✓ Logo present');
  } else {
    console.log('   ✗ Logo missing');
  }

  // Check CTA buttons
  const ctaButtons = await page.locator('a:has-text("Register Now")');
  if (await ctaButtons.count() > 0) {
    console.log('   ✓ CTA buttons present');
  } else {
    console.log('   ✗ CTA buttons missing');
  }

  // Test 2: Committees page
  console.log('\n2. Testing committees page...');
  await page.goto('http://localhost:8000/committees.html');
  await page.waitForLoadState('networkidle');

  // Check table
  const table = await page.locator('table');
  if (await table.count() > 0) {
    console.log('   ✓ Committees table present');
  } else {
    console.log('   ✗ Committees table missing');
  }

  // Check committee rows
  const committeeRows = await page.locator('tbody tr');
  const rowCount = await committeeRows.count();
  console.log(`   ✓ ${rowCount} committee rows loaded`);

  // Test 3: Registration page
  console.log('\n3. Testing registration page...');
  await page.goto('http://localhost:8000/register.html');
  await page.waitForLoadState('networkidle');

  // Check form fields
  const formFields = [
    'full_name',
    'student_id_cnic',
    'email',
    'phone',
    'institution',
    'committee_id'
  ];

  for (const field of formFields) {
    const input = await page.locator(`#${field}`);
    if (await input.count() > 0) {
      console.log(`   ✓ ${field} field present`);
    } else {
      console.log(`   ✗ ${field} field missing`);
    }
  }

  // Test 4: Success page
  console.log('\n4. Testing success page...');
  await page.goto('http://localhost:8000/success.html');
  await page.waitForLoadState('networkidle');

  // Check roll number display
  const rollNumber = await page.locator('#roll-number');
  if (await rollNumber.count() > 0) {
    console.log('   ✓ Roll number display present');
  } else {
    console.log('   ✗ Roll number display missing');
  }

  // Test 5: Navigation
  console.log('\n5. Testing navigation...');

  // Home → Committees
  await page.goto('http://localhost:8000');
  await page.click('a[href="/committees.html"]');
  await page.waitForLoadState('networkidle');
  console.log('   ✓ Home → Committees navigation works');

  // Committees → Register
  await page.click('a[href="/register.html"]');
  await page.waitForLoadState('networkidle');
  console.log('   ✓ Committees → Register navigation works');

  // Register → Home
  await page.click('a[href="/"]');
  await page.waitForLoadState('networkidle');
  console.log('   ✓ Register → Home navigation works');

  console.log('\n✅ All tests completed!');
  console.log('\nFrontend is accessible at: http://localhost:8000');
  console.log('Pages available:');
  console.log('  - Homepage: /');
  console.log('  - Committees: /committees.html');
  console.log('  - Registration: /register.html');
  console.log('  - Success: /success.html');

  await browser.close();
})();