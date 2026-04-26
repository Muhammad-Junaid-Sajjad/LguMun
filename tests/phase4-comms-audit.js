/**
 * PHASE 4: REAL-TIME COMMUNICATIONS & QUERIES AUDIT
 * Tests: Delegate Query System, Tracking ID Generation, Response Polling
 */

const { chromium } = require('playwright');

async function runCommunicationAudit() {
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  console.log('╔════════════════════════════════════════════════════════════╗');
  console.log('║   PHASE 4: COMMUNICATIONS & QUERY SYSTEM AUDIT             ║');
  console.log('║   Target: 110% Stable Communications                       ║');
  console.log('╚════════════════════════════════════════════════════════════╝\n');

  const audit = { passed: 0, failed: 0, issues: [] };

  try {
    // ---------------------------------------------------------
    // SECTION 1: QUERY SUBMISSION FLOW
    // ---------------------------------------------------------
    console.log('📍 SECTION 1: DELEGATE QUERY SUBMISSION --------------');

    // Simulate being on success page after registration
    await page.goto('http://localhost:8000/success.html');
    await page.evaluate(() => {
        sessionStorage.setItem('mun_registration', JSON.stringify({
            roll_number: 'LGU-UNSC-047',
            full_name: 'Comms Tester',
            email: 'comms@test.com',
            committee_name: 'United Nations Security Council'
        }));
    });
    await page.reload();
    await page.waitForTimeout(1500);

    console.log('   [1.1] Verifying Query Portal visibility...');
    const portalVisible = await page.isVisible('.query-portal');
    console.log(`         Portal visible: ${portalVisible ? '✅ PASS' : '❌ FAIL'}`);
    if (portalVisible) audit.passed++; else { audit.failed++; audit.issues.push('Query portal not visible'); }

    console.log('   [1.2] Testing empty message validation...');
    await page.click('#submit-query-btn');
    await page.waitForTimeout(500);
    const resultText = await page.textContent('#query-result');
    const validationWorks = resultText.includes('enter your message');
    console.log(`         Validation working: ${validationWorks ? '✅ PASS' : '❌ FAIL'}`);
    if (validationWorks) audit.passed++; else { audit.failed++; audit.issues.push('Empty message validation failed'); }

    console.log('   [1.3] Submitting a valid query...');
    const testMessage = "Extreme testing query message " + Date.now();
    await page.fill('#query-message', testMessage);
    await page.selectOption('#query-category', 'Technical');
    await page.click('#submit-query-btn');

    // Wait for success message and tracking ID
    await page.waitForSelector('.query-portal div[style*="background"]', { timeout: 10000 });
    const successContent = await page.textContent('#query-result');
    const trackingIdMatch = successContent.match(/QRY-\d{4}-\d{4}/);
    const trackingId = trackingIdMatch ? trackingIdMatch[0] : null;

    console.log(`         Submission successful: ${trackingId ? '✅ PASS' : '❌ FAIL'}`);
    console.log(`         Generated Tracking ID: ${trackingId}`);
    if (trackingId) audit.passed++; else { audit.failed++; audit.issues.push('Failed to generate tracking ID'); }

    // ---------------------------------------------------------
    // SECTION 2: QUERY TRACKING & STATUS
    // ---------------------------------------------------------
    console.log('\n📍 SECTION 2: QUERY TRACKING & RESPONSES -------------');

    console.log('   [2.1] Switching to Check Response tab...');
    await page.click('#check-tab');
    await page.waitForTimeout(500);
    const checkFormVisible = await page.isVisible('#check-form');
    console.log(`         Tab switch working: ${checkFormVisible ? '✅ PASS' : '❌ FAIL'}`);
    if (checkFormVisible) audit.passed++; else { audit.failed++; audit.issues.push('Check tab not showing'); }

    console.log('   [2.2] Checking status of the new query...');
    await page.fill('#query-tracking-id', trackingId);
    await page.click('#check-query-btn');
    await page.waitForTimeout(1000);

    const statusContent = await page.textContent('#query-status');
    const statusValid = statusContent.includes('Pending') || statusContent.includes('SUBMITTED');
    console.log(`         Status check working: ${statusValid ? '✅ PASS' : '❌ FAIL'}`);
    if (statusValid) audit.passed++; else { audit.failed++; audit.issues.push('Status check returned invalid data'); }

    // ---------------------------------------------------------
    // SECTION 3: ADMIN RESPONSE FLOW (API LEVEL)
    // ---------------------------------------------------------
    console.log('\n📍 SECTION 3: ADMIN RESPONSE INTEGRITY --------------');

    console.log('   [3.1] Testing Admin reply via API...');
    // We need the numeric ID of the query from the DB or just find it via tracking ID
    const adminReplyResult = await page.evaluate(async (tid) => {
        // Find the query first
        const adminKey = 'lgumun2026_admin_secure_key_x9y2z';
        const listRes = await fetch('/api/v1/admin/delegate-queries', {
            headers: { 'X-Admin-API-Key': adminKey }
        });
        const listData = await listRes.json();
        const query = listData.data.queries.find(q => q.tracking_id === tid);

        if (!query) return { success: false, error: 'Query not found in admin list' };

        // Reply to it
        const replyRes = await fetch(`/api/v1/admin/delegate-queries/${query.id}/reply`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-API-Key': adminKey
            },
            body: JSON.stringify({ reply: 'This is a test response from Admin Team.' })
        });
        return await replyRes.json();
    }, trackingId);

    console.log(`         Admin reply successful: ${adminReplyResult.success ? '✅ PASS' : '❌ FAIL'}`);
    if (adminReplyResult.success) audit.passed++; else { audit.failed++; audit.issues.push('Admin reply API failed'); }

    console.log('   [3.2] Verifying reply visibility for delegate...');
    await page.click('#check-query-btn'); // Re-check
    await page.waitForTimeout(1500);

    const updatedStatus = await page.textContent('#query-status');
    const hasReply = updatedStatus.includes('Replied') && updatedStatus.includes('test response from Admin Team');
    console.log(`         Reply visible to delegate: ${hasReply ? '✅ PASS' : '❌ FAIL'}`);
    if (hasReply) audit.passed++; else { audit.failed++; audit.issues.push('Delegate cannot see admin reply'); }

    // ---------------------------------------------------------
    // SECTION 4: ANNOUNCEMENTS INTEGRITY
    // ---------------------------------------------------------
    console.log('\n📍 SECTION 4: ANNOUNCEMENTS SYSTEM -------------------');

    console.log('   [4.1] Creating Urgent Announcement via Admin API...');
    const annResult = await page.evaluate(async () => {
        const adminKey = 'lgumun2026_admin_secure_key_x9y2z';
        const res = await fetch('/api/v1/admin/announcements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Admin-API-Key': adminKey
            },
            body: JSON.stringify({
                title: 'Emergency Change',
                message: 'All delegates report to Main Hall immediately!',
                priority: 'urgent',
                target: 'all'
            })
        });
        return await res.json();
    });
    console.log(`         Announcement created: ${annResult.success ? '✅ PASS' : '❌ FAIL'}`);
    if (annResult.success) audit.passed++; else { audit.failed++; audit.issues.push('Announcement creation failed'); }

    console.log('   [4.2] Testing public polling for announcements...');
    const pollResult = await page.evaluate(async () => {
        const res = await fetch('/api/v1/announcements/active');
        return await res.json();
    });
    const hasAnnouncement = pollResult.data.announcements.some(a => a.title === 'Emergency Change');
    console.log(`         Announcement polled: ${hasAnnouncement ? '✅ PASS' : '❌ FAIL'}`);
    if (hasAnnouncement) audit.passed++; else { audit.failed++; audit.issues.push('Public polling cannot see announcement'); }

    // ---------------------------------------------------------
    // FINAL REPORT
    // ---------------------------------------------------------
    console.log('\n╔════════════════════════════════════════════════════════════╗');
    console.log('║               COMMUNICATION AUDIT REPORT                   ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');

    console.log(`   TESTS PASSED: ${audit.passed}`);
    console.log(`   TESTS FAILED: ${audit.failed}`);

    if (audit.failed === 0) {
      console.log('\n   🎉 RESULT: ★★★★★ COMMUNICATION SYSTEM 110% STABLE ★★★★★');
    } else {
      console.log('\n   ⚠️ RESULT: Stability issues detected');
      audit.issues.forEach(i => console.log('      -', i));
    }

    await page.screenshot({ path: 'test-results/phase4-comms-audit.png', fullPage: true });

  } catch (error) {
    console.error('   ❌ AUDIT ERROR:', error.message);
  } finally {
    await browser.close();
    process.exit(audit.failed === 0 ? 0 : 1);
  }
}

runCommunicationAudit();