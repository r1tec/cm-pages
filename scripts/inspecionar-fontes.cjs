// Uso: PUPPETEER_MODULE=/caminho/puppeteer-core node scripts/inspecionar-fontes.cjs URL saida.json
// Coleta também FAQs fechadas. Não publica nem altera a página.
const fs = require('node:fs');
const puppeteer = require(process.env.PUPPETEER_MODULE || 'puppeteer-core');
const [url, output] = process.argv.slice(2);
if (!url || !output) throw new Error('Informe URL e arquivo JSON de saída');
(async () => {
  const browser = await puppeteer.launch({
    executablePath: process.env.CHROME_PATH || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    headless: true,
  });
  try {
    const results = [];
    for (const width of [390, 1440]) {
      const page = await browser.newPage();
      await page.setViewport({width, height: 844});
      await page.goto(url, {waitUntil: 'load'});
      await page.evaluate(() => document.fonts.ready);
      const groups = await page.evaluate(() => {
        const groups = {};
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
          const node = walker.currentNode, el = node.parentElement;
          if (!el || el.closest('script,style,noscript,iframe') || !node.textContent.trim()) continue;
          const css = getComputedStyle(el);
          const family = css.fontFamily.split(',')[0].replaceAll('"', '').replaceAll("'", '').trim();
          const key = family + '/' + css.fontStyle;
          const group = groups[key] ||= {family, style: css.fontStyle, text: '', critical: false, weights: []};
          let text = node.textContent;
          if (css.textTransform === 'uppercase') text = text.toUpperCase();
          else if (css.textTransform === 'lowercase') text = text.toLowerCase();
          else if (css.textTransform === 'capitalize') text = text.replace(/\b\w/g, c => c.toUpperCase());
          group.text += text + ' ';
          if (!group.weights.includes(css.fontWeight)) group.weights.push(css.fontWeight);
          const rect = el.getBoundingClientRect();
          if (rect.width && rect.height && rect.top < innerHeight && rect.bottom > 0) group.critical = true;
        }
        return Object.values(groups);
      });
      results.push({width, name: 'local', state: {groups}});
      await page.close();
    }
    fs.writeFileSync(output, JSON.stringify(results, null, 2));
    console.log(`Inspeção gravada em ${output}`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
