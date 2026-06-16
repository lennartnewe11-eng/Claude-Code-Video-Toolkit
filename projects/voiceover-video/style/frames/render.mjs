import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import path from 'path';

const dir = path.dirname(fileURLToPath(import.meta.url));
const out = path.join(dir, 'out');
const frames = (process.argv[2] ? process.argv.slice(2)
  : ['frame_e1_hook', 'frame_e2_explainer', 'frame_e3_card', 'frame_e4_cutout']);

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
