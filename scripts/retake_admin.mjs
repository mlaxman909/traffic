// Retake admin/users page screenshot — logged in as System Administrator (R. Mehta)
import puppeteer from 'puppeteer';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const outputDir = path.join(__dirname, '..', 'public', 'screenshots');
const BASE_URL  = 'http://localhost:5173';

const sleep = ms => new Promise(r => setTimeout(r, ms));

(async () => {
  console.log('🚀 Launching browser...');
  const browser = await puppeteer.launch({
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,900'],
    defaultViewport: { width: 1440, height: 900 },
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 900 });

  // ── Real login as SYSTEM ADMINISTRATOR ────────────────────────
  console.log('🔐 Logging in as R. Mehta (System Administrator)...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 15000 });
  await sleep(800);

  await page.focus('#email');
  await page.type('#email', 'r.mehta@signalai.gov.in', { delay: 30 });
  await page.focus('#password');
  await page.type('#password', 'password123', { delay: 30 });

  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 }),
    page.keyboard.press('Enter'),
  ]);
  console.log('   After login URL:', page.url());
  await sleep(1500);

  // ── Navigate to Admin Users page ──────────────────────────────
  console.log('👥 Navigating to /admin/users...');
  await page.goto(`${BASE_URL}/admin/users`, { waitUntil: 'networkidle0', timeout: 20000 });
  await sleep(3000);

  const finalUrl = page.url();
  console.log('   Final URL:', finalUrl);

  const savePath = path.join(outputDir, 'admin_users.png');
  await page.screenshot({ path: savePath, fullPage: true });
  const size = fs.statSync(savePath).size;
  console.log(`\n✅ admin_users.png → ${(size/1024).toFixed(1)} KB`);

  await browser.close();
})();
