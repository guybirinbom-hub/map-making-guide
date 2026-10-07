// Usage: node render.js <svg> <out.png> [scale] [cropX cropY cropW cropH]
// Renders the SVG with Chromium, writes a PNG, and reports overlapping labels
// (measured with the real font) as JSON on stdout.
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node-tools/node_modules/playwright');
const fs = require('fs');

(async () => {
  const [svgPath, out, scaleArg, cx, cy, cw, ch] = process.argv.slice(2);
  const scale = parseFloat(scaleArg || '1.5');
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  });
  const page = await browser.newPage({
    viewport: { width: 1000, height: 800 },
    deviceScaleFactor: scale,
  });
  const svg = fs.readFileSync(svgPath, 'utf8');
  await page.setContent(
    `<html><body style="margin:0;background:#0d1117">${svg}</body></html>`
  );
  await page.evaluate(() => {
    const s = document.querySelector('svg');
    s.setAttribute('width', '1000');
    s.setAttribute('height', '800');
    s.style.display = 'block';
  });
  const clip = cx
    ? { x: +cx, y: +cy, width: +cw, height: +ch }
    : { x: 0, y: 0, width: 1000, height: 800 };
  await page.screenshot({ path: out, clip });

  const report = await page.evaluate(() => {
    // oriented boxes: 4 corners in screen space
    const quad = (el) => {
      const b = el.getBBox();
      const m = el.getScreenCTM();
      const pt = (x, y) => ({ x: m.a * x + m.c * y + m.e, y: m.b * x + m.d * y + m.f });
      return [pt(b.x, b.y), pt(b.x + b.width, b.y), pt(b.x + b.width, b.y + b.height), pt(b.x, b.y + b.height)];
    };
    const shrink = (q, m) => {
      const cx = (q[0].x + q[2].x) / 2, cy = (q[0].y + q[2].y) / 2;
      return q.map(p => {
        const dx = p.x - cx, dy = p.y - cy, L = Math.hypot(dx, dy) || 1;
        return { x: p.x - dx / L * m, y: p.y - dy / L * m };
      });
    };
    const axes = (q) => [0, 1].map(i => {
      const a = q[i], b = q[i + 1];
      return { x: -(b.y - a.y), y: b.x - a.x };
    });
    const proj = (q, ax) => {
      const v = q.map(p => p.x * ax.x + p.y * ax.y);
      return [Math.min(...v), Math.max(...v)];
    };
    const sat = (A, B) => {
      for (const ax of [...axes(A), ...axes(B)]) {
        const [a0, a1] = proj(A, ax), [b0, b1] = proj(B, ax);
        if (a1 <= b0 || b1 <= a0) return false;
      }
      return true;
    };
    const texts = [];
    for (const t of document.querySelectorAll('text')) {
      if (t.closest('[data-nocheck]')) continue;
      const q = quad(t);
      const blk = t.closest('[data-block]');
      // vertical extent of getBBox includes the full font ascent/descent; trim it a bit
      texts.push({ s: t.textContent, q: shrink(q, 0.9), blk });
    }
    const syms = [];
    for (const g of document.querySelectorAll('[data-sym]')) {
      syms.push({ s: g.getAttribute('data-sym'), q: shrink(quad(g), 0.5) });
    }
    const textText = [];
    for (let i = 0; i < texts.length; i++)
      for (let j = i + 1; j < texts.length; j++) {
        if (texts[i].blk && texts[i].blk === texts[j].blk) continue;
        if (sat(texts[i].q, texts[j].q)) textText.push([texts[i].s, texts[j].s]);
      }
    const textSym = [];
    for (const t of texts)
      for (const s of syms)
        if (sat(t.q, s.q)) textSym.push([t.s, s.s]);
    const outside = texts.filter(t => t.q.some(p => p.x < 0 || p.y < 0 || p.x > 1000 || p.y > 800)).map(t => t.s);
    return { nText: texts.length, nSym: syms.length, textText, textSym, outside };
  });
  console.log(JSON.stringify(report, null, 1));
  await browser.close();
})();
