import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(dir, 'out');
const frames = ['frame_01_hook', 'frame_02_chart', 'frame_03_archival'];

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
import { mkdirSync } from 'fs';
mkdirSync(out, { recursive: true });
for (const f of frames) {
  await page.goto('file://' + path.join(dir, f + '.html'));
  await page.waitForTimeout(400); // let font + layout settle
  await page.screenshot({ path: path.join(out, f + '.png') });
  console.log('rendered', f);
}
await browser.close();
