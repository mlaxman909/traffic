// Takes a proper traffic map screenshot by doing a REAL login via the form
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

  // ── Step 1: Real login via form ─────────────────────────────────
  console.log('🔐 Loading login page...');
  await page.goto(`${BASE_URL}/login`, { waitUntil: 'networkidle0', timeout: 15000 });
  await sleep(1000);

  // Fill email
  await page.focus('#email');
  await page.type('#email', 'j.sharma@signalai.gov.in', { delay: 30 });

  // Fill password
  await page.focus('#password');
  await page.type('#password', 'password123', { delay: 30 });

  console.log('   Submitting login form...');
  await Promise.all([
    page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 15000 }),
    page.keyboard.press('Enter'),
  ]);

  const afterLoginUrl = page.url();
  console.log('   After login URL:', afterLoginUrl);

  if (!afterLoginUrl.includes('/dashboard') && !afterLoginUrl.includes('/traffic')) {
    console.log('   ⚠️  Still on login? Trying button click...');
    await page.click('button[type="submit"]');
    await page.waitForNavigation({ waitUntil: 'networkidle0', timeout: 10000 }).catch(() => {});
    console.log('   URL now:', page.url());
  }

  await sleep(2000);

  // ── Step 2: Navigate to Traffic Map ────────────────────────────
  console.log('🗺️  Navigating to /traffic-map...');
  await page.goto(`${BASE_URL}/traffic-map`, { waitUntil: 'networkidle0', timeout: 25000 });

  // Wait for sidebar (means app rendered successfully)
  await page.waitForSelector('[class*="sidebar"], [class*="Sidebar"], nav', { timeout: 10000 })
    .then(() => console.log('   ✅ Sidebar rendered'))
    .catch(() => console.log('   ⚠️  Sidebar selector not matched'));

  console.log('⏳ Waiting 8s for map tiles...');
  await sleep(8000);

  const finalUrl = page.url();
  console.log('   Final URL:', finalUrl);

  const savePath = path.join(outputDir, 'traffic_map.png');
  await page.screenshot({ path: savePath, fullPage: true });
  const size = fs.statSync(savePath).size;
  console.log(`\n✅ traffic_map.png → ${(size/1024).toFixed(1)} KB`);
  console.log(size > 100000 ? '🎉 Looks like real content!' : '⚠️  Small file — may be blank');

  await browser.close();
})();
