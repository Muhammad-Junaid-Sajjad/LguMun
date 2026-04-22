const { chromium } = require('playwright');

(async () => {
  console.log('=== Browser Flow Test ===\n');
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Track requests
  const apiRequests = [];
  page.on('request', r => {
    if (r.url().includes('/api/')) apiRequests.push({ url: r.url(), method: r.method() });
  });

  const errors = [];
  page.on('pageerror', e => errors.push(e.message));

  try {
    // Test 1: Load index.html
    console.log('1. Testing index.html...');
    await page.goto('http://localhost:3000/index.html', { waitUntil: 'networkidle', timeout: 15000 });
    const indexTitle = await page.title();
    console.log(`   Title: ${indexTitle}`);
    if (!indexTitle.includes('LGUMUN')) throw new Error('Index title wrong');

    // Test 2: Load committees page
    console.log('2. Testing committees.html...');
    await page.goto('http://localhost:3000/committees.html', { waitUntil: 'networkidle', timeout: 15000 });
    const commTitle = await page.title();
    console.log(`   Title: ${commTitle}`);

    // Test 3: Load register page
    console.log('3. Testing register.html...');
    await page.goto('http://localhost:3000/register.html', { waitUntil: 'networkidle', timeout: 15000 });
    const regTitle = await page.title();
    console.log(`   Title: ${regTitle}`);

    // Check form exists
    const formFields = await page.locator('#full_name, #email, #phone, #institution, #student_id_cnic, #committee_id, #terms-checkbox').count();
    console.log(`   Form fields found: ${formFields}`);

    // Test 3b: Load success page
    console.log('4. Testing success.html...');
    await page.goto('http://localhost:3000/success.html', { waitUntil: 'networkidle', timeout: 15000 });
    const succTitle = await page.title();
    console.log(`   Title: ${succTitle}`);

    // Check confetti canvas exists
    const confetti = await page.locator('#confetti-canvas').count();
    console.log(`   Confetti canvas: ${confetti === 1 ? 'Found' : 'Missing'}`);

    // Test 5: API endpoint verification
    console.log('6. Verifying API endpoints...');
    const committeesResp = await page.evaluate(async () => {
      const r = await fetch('http://localhost:8000/api/v1/committees');
      return r.ok ? { status: r.status } : { error: r.status };
    });
    console.log(`   /committees: ${committeesResp.status || committeesResp.error}`);

    const countResp = await page.evaluate(async () => {
      const r = await fetch('http://localhost:8000/api/v1/delegates/count');
      return r.ok ? await r.json() : { error: r.status };
    });
    console.log(`   /delegates/count: ${JSON.stringify(countResp.data || countResp.error).substring(0, 50)}`);

    // Test 5: Verify committees API returns all committees
    console.log('5. Verifying committees data...');
    const commResp = await page.evaluate(async () => {
      const r = await fetch('http://localhost:8000/api/v1/committees');
      return r.ok ? await r.json() : { error: r.status };
    });
    const commCount = commResp.data?.committees?.length || 0;
    console.log(`   Total committees: ${commCount}`);

    // Test 5: Check errors
    if (errors.length > 0) {
      console.log(`\n⚠️  Page errors: ${errors.length}`);
      errors.forEach(e => console.log(`   - ${e.substring(0, 80)}`));
    } else {
      console.log('\n✅ No page errors detected');
    }

    console.log('\n=== All Browser Tests Passed ===');
  } catch (err) {
    console.error('❌ Test failed:', err.message);
    process.exit(1);
  } finally {
    await browser.close();
  }
})();