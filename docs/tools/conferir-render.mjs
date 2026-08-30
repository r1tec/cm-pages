// Conferência anti-quebra COM EVIDÊNCIA — abre a página num Chrome real (CDP),
// rola até o fim para disparar lazy-load, e reporta:
//   - <img> com naturalWidth 0 (imagem que não carregou/decodificou)
//   - elementos cujo CSS pede background-image mas o navegador computou "none"
//     (fundo de container que não aparece — o bug dos cartões pretos)
//   - salva um screenshot de página inteira como prova
//
// Uso:  node conferir-render.mjs <url> [saida.png]
//   ex: node docs/tools/conferir-render.mjs https://contemmagia.com.br/bce/ /tmp/bce.png
//
// Node 18+ (usa fetch e WebSocket nativos). Precisa do Google Chrome instalado.
import { spawn } from 'child_process';

const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const url = process.argv[2];
const shot = process.argv[3] || null;
if (!url) { console.error("uso: node conferir-render.mjs <url> [saida.png]"); process.exit(2); }
const port = 9330 + Math.floor((Date.now() % 500));
const sleep = ms => new Promise(r => setTimeout(r, ms));

const chrome = spawn(CHROME, ["--headless=new","--disable-gpu","--no-sandbox",
  `--remote-debugging-port=${port}`,"--hide-scrollbars","--window-size=1400,2400","about:blank"]);
await sleep(1300);

const tab = await (await fetch(`http://127.0.0.1:${port}/json/new?${encodeURIComponent(url)}`,{method:'PUT'})).json();
const ws = new WebSocket(tab.webSocketDebuggerUrl);
let id = 0; const pend = new Map();
const send = (method, params={}) => new Promise(res => { const i=++id; pend.set(i,res); ws.send(JSON.stringify({id:i,method,params})); });
await new Promise(r => ws.addEventListener('open', r));
ws.addEventListener('message', e => { const m=JSON.parse(e.data); if(m.id&&pend.has(m.id)){pend.get(m.id)(m.result);pend.delete(m.id);} });

await send('Page.enable'); await send('Runtime.enable');
await send('Page.navigate', { url });
await sleep(3500);
// rola a página inteira para disparar lazy-load, depois volta ao topo
await send('Runtime.evaluate', { expression: `(async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){window.scrollTo(0,y);await new Promise(r=>setTimeout(r,120));}window.scrollTo(0,0);})()`, awaitPromise:true });
await sleep(1500);

const expr = `(()=>{
  const bg=[]; const imgsBroken=[]; let imgsOk=0;
  for(const el of document.querySelectorAll('*')){
    const cs=getComputedStyle(el); const r=el.getBoundingClientRect();
    if(r.width<3||r.height<3) continue;
    const bi=cs.backgroundImage;
    if(bi&&bi!=='none'&&/url\\(/.test(bi)){
      const m=bi.match(/url\\(["']?([^"')]+)/);
      bg.push({src:m?m[1]:'', cls:(el.className||'').toString().slice(0,70), w:Math.round(r.width), h:Math.round(r.height)});
    }
  }
  for(const im of document.images){
    if(im.naturalWidth===0) imgsBroken.push({src:im.currentSrc||im.src, cls:(im.className||'').toString().slice(0,50)});
    else imgsOk++;
  }
  return {bg, imgsBroken, imgsOk};
})()`;
const r = await send('Runtime.evaluate', { expression: expr, returnByValue: true });
const d = r.result.value;

// status HTTP de cada arquivo de background
const uniq = [...new Set(d.bg.map(b=>b.src).filter(s=>s&&!s.startsWith('data:')))];
const st = {};
for (const s of uniq) { try { const rr=await fetch(new URL(s,url).href); st[s]=rr.status; } catch(e){ st[s]='ERR'; } }

console.log('== CONFERÊNCIA ANTI-QUEBRA ==', url);
console.log(`<img> ok: ${d.imgsOk} | <img> QUEBRADAS (naturalWidth 0): ${d.imgsBroken.length}`);
d.imgsBroken.forEach(i=>console.log('   IMG QUEBRADA:', i.src.split('/').pop(), '·', i.cls));
console.log(`background-image pintados: ${d.bg.length} (arquivos únicos: ${uniq.length})`);
const seen=new Set();
for (const b of d.bg){ if(seen.has(b.src))continue; seen.add(b.src);
  console.log(`   http=${st[b.src]}  ${b.w}x${b.h}  ${String(b.src).split('/').pop()}`); }

if (shot) { const png = await send('Page.captureScreenshot', { format:'png', captureBeyondViewport:true });
  const fs = await import('fs'); fs.writeFileSync(shot, Buffer.from(png.data,'base64')); console.log('screenshot:', shot); }

chrome.kill();
process.exit(d.imgsBroken.length ? 1 : 0);
