// Usage: node render_mermaid.js <in.mmd> <out.png> [scale]
// Renders a Mermaid diagram to PNG with Chromium (used by build_pdf.py).
const { chromium } = require(process.env.PLAYWRIGHT_MODULE || '/opt/node-tools/node_modules/playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const [src, out, scaleArg] = process.argv.slice(2);
  const code = fs.readFileSync(src, 'utf8');
  const lib = path.resolve(__dirname, 'build', 'mermaid.min.js');
  const html = `<!doctype html><html><head><meta charset="utf-8">
<style>body{margin:0;background:#fff} #d{display:inline-block;padding:8px}</style>
<script src="file://${lib}"></script></head><body><div id="d"><pre class="mermaid"></pre></div>
<script>
document.querySelector('.mermaid').textContent = ${JSON.stringify(code)};
mermaid.initialize({ startOnLoad: false, theme: 'base', fontFamily: 'Alegreya Sans, DejaVu Sans, sans-serif',
  themeVariables: { primaryColor: '#e8f0f1', primaryBorderColor: '#1d5560', primaryTextColor: '#24211c',
    lineColor: '#6b6358', clusterBkg: '#f7f4ee', clusterBorder: '#b9ad9a', fontSize: '15px' },
  flowchart: { curve: 'basis', padding: 12 } });
mermaid.run().then(() => { window.done = true; });
</script></body></html>`;
  const tmp = path.resolve(__dirname, 'build', 'mermaid-page.html');
  fs.writeFileSync(tmp, html);
  const browser = await chromium.launch({
    executablePath: process.env.CHROMIUM_PATH || '/opt/pw-browsers/chromium-1194/chrome-linux/chrome',
  });
  const page = await browser.newPage({ deviceScaleFactor: parseFloat(scaleArg || '3') });
  await page.goto('file://' + tmp);
  await page.waitForFunction('window.done === true', null, { timeout: 30000 });
  const el = await page.$('#d');
  await el.screenshot({ path: out });
  await browser.close();
})();
