/**
 * Retakes screenshots for all pages using a TALL viewport (1440x1200)
 * instead of fullPage:true — this avoids the fixed-sidebar gap issue.
 *
 * Strategy:
 *  - Set viewport tall enough to fit most pages without scrolling
 *  - Use fullPage:false so fixed elements (sidebar) render correctly
 *  - For pages that might still be taller, we measure and resize the viewport first
 */
import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outputDir = path.join(__dirname, '..', 'public', 'screenshots');
const BASE_URL  = 'http://localhost:5173';

const sleep = ms => new Promise(r => setTimeout(r, ms));

/** Navigate with auth + dynamic viewport height to avoid sidebar gap */
async function smartScreenshot(page, url, filename, extraWait = 2500) {
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 20000 });
  await sleep(extraWait);

  // Measure how tall the main content area is
  const pageHeight = await page.evaluate(() => {
    const main = document.querySelector('main, [class*="content"], [class*="Content"]');
    if (main) {
      return Math.max(main.scrollHeight + 80, window.innerHeight);
    }
    return document.body.scrollHeight;
  });

  const clampedHeight = Math.min(Math.max(pageHeight, 900), 1800);
  await page.setViewport({ width: 1440, height: clampedHeight });
  await sleep(300); // allow reflow

  const savePath = path.join(outputDir, filename);
  // fullPage: false — lets fixed sidebar render without gap
  await page.screenshot({ path: savePath, fullPage: false });
  const size = fs.statSync(savePath).size;
  console.log(`   ✅ ${filename} (${(size/1024).toFixed(1)} KB, viewport h=${clampedHeight})`);
}

(async () => {
  console.log('🚀 Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,1400'],
    defaultViewport: { width: 1440, height: 1200 },
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 1200 });

  // ── 1. Login (public page — no sidebar) ───────────────────────
  console.log('\n📸 Login...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 15000 });
  await sleep(1500);
  await page.setViewport({ width: 1440, height: 900 });
  await page.screenshot({ path: path.join(outputDir, 'login.png'), fullPage: false });
  console.log('   ✅ login.png');

  // ── Real login as J. Sharma ────────────────────────────────────
  console.log('\n🔐 Logging in as J. Sharma...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0' });
  await page.setViewport({ width: 1440, height: 900 });
  await sleep(800);
  await page.focus('#email');
  await page.type('#email', 'j.sharma@signalai.gov.in', { delay: 25 });
  await page.focus('#password');
  await page.type('#password', 'password123', { delay: 25 });
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 }),
    page.keyboard.press('Enter'),
  ]);
  console.log('   Logged in →', page.url());
  await sleep(1000);

  // ── 2. Dashboard ────────────────────────────────────────────────
  console.log('\n📸 Dashboard...');
  await smartScreenshot(page, `${BASE_URL}/dashboard`, 'dashboard.png', 3000);

  // ── 3. Traffic Map ──────────────────────────────────────────────
  console.log('\n📸 Traffic Map...');
  await page.setViewport({ width: 1440, height: 900 });
  await page.goto(`${BASE_URL}/traffic-map`, { waitUntil: 'networkidle0', timeout: 25000 });
  await sleep(8000); // wait for map tiles
  await page.screenshot({ path: path.join(outputDir, 'traffic_map.png'), fullPage: false });
  const mapSize = fs.statSync(path.join(outputDir, 'traffic_map.png')).size;
  console.log(`   ✅ traffic_map.png (${(mapSize/1024).toFixed(1)} KB)`);

  // ── 4. Analytics ────────────────────────────────────────────────
  console.log('\n📸 Analytics...');
  await page.setViewport({ width: 1440, height: 900 });
  await smartScreenshot(page, `${BASE_URL}/analytics`, 'analytics.png', 3000);

  // ── 5. Decision Queue ───────────────────────────────────────────
  console.log('\n📸 Decision Queue...');
  await page.setViewport({ width: 1440, height: 900 });
  await smartScreenshot(page, `${BASE_URL}/decision-queue`, 'decision_queue.png', 2500);

  // ── 6. Emergency Routing ────────────────────────────────────────
  console.log('\n📸 Emergency Routing...');
  await page.setViewport({ width: 1440, height: 900 });
  await smartScreenshot(page, `${BASE_URL}/emergency-routing`, 'emergency_routing.png', 2500);

  // ── 7. Assistant ────────────────────────────────────────────────
  console.log('\n📸 Assistant...');
  await page.setViewport({ width: 1440, height: 900 });
  await smartScreenshot(page, `${BASE_URL}/assistant`, 'assistant.png', 2500);

  // ── 8. Settings ─────────────────────────────────────────────────
  console.log('\n📸 Settings...');
  await page.setViewport({ width: 1440, height: 900 });
  await smartScreenshot(page, `${BASE_URL}/settings`, 'settings.png', 2500);

  // ── 9. Admin Users (as System Administrator) ────────────────────
  console.log('\n📸 Admin Users (logging in as R. Mehta)...');
  // Switch to admin account
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0' });
  await page.evaluate(() => localStorage.clear());
  await sleep(500);
  await page.focus('#email');
  await page.type('#email', 'r.mehta@signalai.gov.in', { delay: 25 });
  await page.focus('#password');
  await page.type('#password', 'password123', { delay: 25 });
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 }),
    page.keyboard.press('Enter'),
  ]);
  await sleep(1000);
  await page.setViewport({ width: 1440, height: 900 });
  await smartScreenshot(page, `${BASE_URL}/admin/users`, 'admin_users.png', 2500);

  await browser.close();

  console.log('\n\n🎉 All screenshots done!');
  fs.readdirSync(outputDir).filter(f => f.endsWith('.png')).forEach(f => {
    const size = fs.statSync(path.join(outputDir, f)).size;
    console.log(`   📄 ${f}  →  ${(size/1024).toFixed(1)} KB`);
  });
})();
