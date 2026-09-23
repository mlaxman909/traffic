import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outputDir = path.join(__dirname, '..', 'public', 'screenshots');

if (!fs.existsSync(outputDir)) {
  fs.mkdirSync(outputDir, { recursive: true });
}

const BASE_URL = 'http://localhost:5173';

// Real JWT obtained from backend: POST /api/auth/login
const REAL_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzkwMTYzNzM5fQ.cbrheMBfXX1qaRYMMlsq_jn_Vu8Cmwq7QpDwFd4Jgk8';

async function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// Navigate to a page with auth token pre-set in localStorage
async function gotoProtected(page, url) {
  // First navigate to base to set localStorage
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'domcontentloaded', timeout: 15000 });
  await page.evaluate((token) => {
    localStorage.setItem('token', token);
  }, REAL_TOKEN);
  // Now navigate to the actual page
  await page.goto(url, { waitUntil: 'networkidle0', timeout: 20000 });
  await sleep(3000);
}

(async () => {
  console.log('🚀 Launching browser...');
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=1440,900',
    ],
    defaultViewport: { width: 1440, height: 900 },
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  // ── 1. LOGIN PAGE ──────────────────────────────────────────────
  console.log('📸 Login page...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 15000 });
  await sleep(2000);
  await page.screenshot({ path: path.join(outputDir, 'login.png'), fullPage: true });
  console.log('   ✅ login.png');

  // ── 2. DASHBOARD ───────────────────────────────────────────────
  console.log('📸 Dashboard...');
  await gotoProtected(page, `${BASE_URL}/dashboard`);
  await page.screenshot({ path: path.join(outputDir, 'dashboard.png'), fullPage: true });
  console.log('   ✅ dashboard.png');

  // ── 3. TRAFFIC MAP ─────────────────────────────────────────────
  console.log('📸 Traffic Map...');
  await gotoProtected(page, `${BASE_URL}/traffic-map`);
  await page.screenshot({ path: path.join(outputDir, 'traffic_map.png'), fullPage: true });
  console.log('   ✅ traffic_map.png');

  // ── 4. ANALYTICS ───────────────────────────────────────────────
  console.log('📸 Analytics...');
  await gotoProtected(page, `${BASE_URL}/analytics`);
  await page.screenshot({ path: path.join(outputDir, 'analytics.png'), fullPage: true });
  console.log('   ✅ analytics.png');

  // ── 5. DECISION QUEUE ──────────────────────────────────────────
  console.log('📸 Decision Queue...');
  await gotoProtected(page, `${BASE_URL}/decision-queue`);
  await page.screenshot({ path: path.join(outputDir, 'decision_queue.png'), fullPage: true });
  console.log('   ✅ decision_queue.png');

  // ── 6. EMERGENCY ROUTING ───────────────────────────────────────
  console.log('📸 Emergency Routing...');
  await gotoProtected(page, `${BASE_URL}/emergency-routing`);
  await page.screenshot({ path: path.join(outputDir, 'emergency_routing.png'), fullPage: true });
  console.log('   ✅ emergency_routing.png');

  // ── 7. ASSISTANT ───────────────────────────────────────────────
  console.log('📸 Assistant...');
  await gotoProtected(page, `${BASE_URL}/assistant`);
  await page.screenshot({ path: path.join(outputDir, 'assistant.png'), fullPage: true });
  console.log('   ✅ assistant.png');

  // ── 8. SETTINGS ────────────────────────────────────────────────
  console.log('📸 Settings...');
  await gotoProtected(page, `${BASE_URL}/settings`);
  await page.screenshot({ path: path.join(outputDir, 'settings.png'), fullPage: true });
  console.log('   ✅ settings.png');

  // ── 9. ADMIN USERS ─────────────────────────────────────────────
  console.log('📸 Admin Users...');
  await gotoProtected(page, `${BASE_URL}/admin/users`);
  await page.screenshot({ path: path.join(outputDir, 'admin_users.png'), fullPage: true });
  console.log('   ✅ admin_users.png');

  await browser.close();

  console.log('\n🎉 All screenshots saved to:', outputDir);
  const files = fs.readdirSync(outputDir).filter(f => f.endsWith('.png'));
  files.forEach(f => {
    const size = fs.statSync(path.join(outputDir, f)).size;
    console.log(`   📄 ${f} (${(size / 1024).toFixed(1)} KB)`);
  });
})();
