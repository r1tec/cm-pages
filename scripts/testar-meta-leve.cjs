// Contrato do envio leve e do engajamento. Sem rede: Image/sendBeacon/SDK simulados.
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = readFileSync(join(__dirname, '..', 'meta-pageview-antecipado.js'), 'utf8');
const ids = ['197461362094441', '884049927923756'];

function setup({cfg, host = 'contemmagia.com.br', search = '', cookie = '', beacon = true} = {}) {
  const hits = [], beacons = [], scripts = [], sent = [], timers = [], listeners = {};
  let jar = cookie;
  const d = {
    referrer: 'https://l.facebook.com/', readyState: 'complete', visibilityState: 'visible',
    get cookie() { return jar; },
    set cookie(v) {
      const [pair, ...attrs] = v.split(';');
      const domain = (attrs.find(a => a.startsWith('domain=')) || '').slice(7);
      if (domain && !('.' + host).endsWith(domain)) return;  // navegador recusa domínio alheio
      if (domain.split('.').filter(Boolean).length < 2) return;
      const name = pair.split('=')[0];
      jar = jar.split('; ').filter(c => c && !c.startsWith(name + '=')).concat(pair).join('; ');
    },
    createElement: () => ({}),
    getElementsByTagName: () => [{parentNode: {insertBefore: s => scripts.push(s)}}],
    addEventListener: () => {}, querySelector: () => null
  };
  const w = {
    __cmMetaCfg: cfg,
    location: {hostname: host, href: 'https://' + host + '/drb/' + search, search},
    screen: {width: 390, height: 844},
    navigator: beacon ? {sendBeacon: (url, blob) => { beacons.push([url, blob]); return true; }} : {},
    Blob: function (parts) { this.text = parts.join(''); },
    Image: function () { const img = {}; hits.push(img); return img; },
    setTimeout: (fn, ms) => { timers.push([fn, ms]); return timers.length; },
    clearTimeout: () => {},
    addEventListener: (e, fn) => { (listeners[e] = listeners[e] || []).push(fn); }
  };
  vm.runInContext(source, vm.createContext({window: w, document: d, Date, Math, RegExp, String, encodeURIComponent, decodeURIComponent}));
  const sdk = () => {
    w.fbq.callMethod = function () { sent.push(Array.from(arguments)); };
    w.fbq.queue.splice(0).forEach(a => w.fbq.callMethod.apply(w.fbq, a));
  };
  const gtm = () => ids.forEach(id => {
    w.fbq('consent', 'grant'); w.fbq('init', id, {});
    w.fbq('set', 'agent', 'tmSimo-GTM-WebTemplate', id); w.fbq('trackSingle', id, 'PageView', {});
  });
  const fire = e => (listeners[e] || []).forEach(fn => fn());
  const params = img => new URLSearchParams(img.src.split('?')[1]);
  return {w, d, hits, beacons, scripts, sent, timers, sdk, gtm, fire, params, jar: () => jar};
}
const pageViews = s => s.sent.filter(a => a[0] === 'trackSingle' && a[2] === 'PageView').length;

// 1. Envio leve: 1 hit por pixel na hora, cookies no formato do SDK, SDK adiado, sem PageView repetido.
{
  const s = setup({cfg: {envio_leve: true}, search: '?utm_source=FB&fbclid=IwAbc_123'});
  assert.equal(s.hits.length, 2);
  assert.deepEqual(s.hits.map(h => s.params(h).get('id')), ids);
  const p = s.params(s.hits[0]);
  assert.equal(p.get('ev'), 'PageView');
  assert.match(p.get('fbp'), /^fb\.2\.\d+\.\d+$/);
  assert.match(p.get('fbc'), /^fb\.2\.\d+\.IwAbc_123$/);
  assert.equal(p.get('dl'), 'https://contemmagia.com.br/drb/?utm_source=FB&fbclid=IwAbc_123');
  assert.equal(p.get('rl'), 'https://l.facebook.com/');
  assert.ok(s.jar().includes('_fbp=' + p.get('fbp')) && s.jar().includes('_fbc=' + p.get('fbc')));
  assert.equal(s.scripts.length, 0, 'SDK não pode carregar na abertura');
  assert.ok(s.timers.some(t => t[1] === 5000));
  s.fire('touchstart'); s.timers.filter(t => t[1] === 1 || t[1] === 5000).forEach(t => t[0]());
  assert.equal(s.scripts.length, 1, 'SDK carrega uma vez após interação/5s');
  s.gtm(); s.sdk();
  assert.equal(pageViews(s), 0, 'SDK/GTM não repetem a visita');
  ids.forEach(id => assert.equal(s.sent.filter(a => a[0] === 'init' && a[1] === id).length, 1));
  s.w.fbq('trackSingle', ids[0], 'Lead', {value: 1});
  assert.equal(s.sent.at(-1)[2], 'Lead');
  s.w.fbq('trackSingle', ids[0], 'PageView', {});
  assert.equal(pageViews(s), 1, 'visita posterior (SPA/tag) preservada');
  console.log('PASS: envio leve — 2 hits, fbp/fbc, SDK adiado, sem PageView duplicado');
}
// 2. Cookies existentes são reaproveitados; fbclid novo atualiza _fbc.
{
  const s = setup({cfg: {envio_leve: true}, search: '?fbclid=novo',
    cookie: '_fbp=fb.2.1700000000000.123456; _fbc=fb.2.1700000000000.antigo'});
  const p = s.params(s.hits[0]);
  assert.equal(p.get('fbp'), 'fb.2.1700000000000.123456');
  assert.match(p.get('fbc'), /^fb\.2\.\d+\.novo$/);
  const same = setup({cfg: {envio_leve: true}, cookie: '_fbc=fb.2.1700000000000.antigo'});
  assert.equal(same.params(same.hits[0]).get('fbc'), 'fb.2.1700000000000.antigo');
  assert.match(same.params(same.hits[0]).get('fbp'), /^fb\.2\./);
  console.log('PASS: cookies existentes reaproveitados; fbclid novo atualiza _fbc');
}
// 3. Cookie recusado (ex.: localhost) → volta ao fluxo antigo pelo SDK, sem hit leve.
{
  const s = setup({cfg: {envio_leve: true}, host: 'localhost'});
  assert.equal(s.hits.length + s.beacons.length, 0);
  assert.equal(s.scripts.length, 1);
  s.sdk(); s.gtm();
  assert.equal(pageViews(s), 2);
  console.log('PASS: sem cookie primário, fallback para SDK com 1 PageView por pixel');
}
// 4. URL longa usa sendBeacon; sem sendBeacon, fallback SDK.
{
  const long = '?fbclid=' + 'x'.repeat(1900);
  const s = setup({cfg: {envio_leve: true}, search: long});
  assert.equal(s.hits.length, 0); assert.equal(s.beacons.length, 2);
  assert.ok(s.beacons[0][1].text.includes('rqm=SB') && s.beacons[0][1].text.includes('ev=PageView'));
  assert.equal(s.scripts.length, 0);
  const nb = setup({cfg: {envio_leve: true}, search: long, beacon: false});
  assert.equal(nb.scripts.length, 1); nb.sdk(); assert.equal(pageViews(nb), 2);
  console.log('PASS: URL longa via sendBeacon; sem beacon, fallback SDK');
}
// 5. Sem envio_leve: comportamento antecipado anterior intacto.
{
  const s = setup({cfg: {oferta: 'texto:R$ 39,90'}});
  assert.equal(s.hits.length, 0); assert.equal(s.scripts.length, 1);
  s.sdk(); s.gtm(); assert.equal(pageViews(s), 2);
  console.log('PASS: modo antecipado sem envio leve inalterado');
}
// 6. Leitura30s: exige 30s visíveis + interação; uma vez só.
{
  const s = setup({cfg: {}});
  s.sdk();
  const custom = () => s.sent.filter(a => a[0] === 'trackCustom' && a[1] === 'Leitura30s').length;
  const realNow = Date.now; let t = realNow();
  Date.now = () => t;
  try {
    const runTicks = n => { for (let i = 0; i < n; i++) { const tk = s.timers.filter(x => x[1] === 1000).pop(); t += 1000; tk[0](); } };
    runTicks(31);
    assert.equal(custom(), 0, 'sem interação não conta');
    s.fire('scroll');
    assert.equal(custom(), 1);
    s.fire('scroll'); s.fire('click');
    assert.equal(custom(), 1);
  } finally { Date.now = realNow; }
  console.log('PASS: Leitura30s exige interação e dispara uma vez');
}
