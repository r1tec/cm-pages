// Contrato do piloto com o template Meta GTM v28. Sem rede/eventos de produção.
const {readFileSync} = require('node:fs');
const {join} = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = readFileSync(join(__dirname, '..', 'meta-pageview-antecipado.js'), 'utf8');
const ids = ['197461362094441', '884049927923756'];
function setup(existing) {
  const scripts = [], sent = [];
  const w = existing ? {fbq: existing} : {};
  const d = {createElement: () => ({}), getElementsByTagName: () => [
    {parentNode: {insertBefore: s => scripts.push(s)}}
  ]};
  const context = vm.createContext({window: w, document: d});
  vm.runInContext(source, context);
  const sdk = () => {
    w.fbq.callMethod = function () {sent.push(Array.from(arguments));};
    const queue = w.fbq.queue.splice(0);
    queue.forEach(a => w.fbq.callMethod.apply(w.fbq, a));
  };
  // Sequência real do template, sem editar seus controles internos.
  const gtm = () => ids.forEach(id => {
    w.fbq('consent', 'grant');
    w.fbq('init', id, {});
    w.fbq('set', 'agent', 'tmSimo-GTM-WebTemplate', id);
    w.fbq('trackSingle', id, 'PageView', {});
  });
  return {w, scripts, sent, context, sdk, gtm};
}
for (const order of ['SDK antes do GTM', 'GTM antes do SDK']) {
  const s = setup();
  if (order.startsWith('SDK')) {s.sdk(); s.gtm();} else {s.gtm(); s.sdk();}
  ids.forEach(id => {
    assert.equal(s.sent.filter(a => a[0] === 'init' && a[1] === id).length, 1);
    assert.equal(s.sent.filter(a => a[0] === 'trackSingle' && a[1] === id && a[2] === 'PageView').length, 1);
    s.w.fbq('trackSingle', id, 'PageView', {});
    assert.equal(s.sent.filter(a => a[0] === 'trackSingle' && a[1] === id && a[2] === 'PageView').length, 2);
  });
  const calls = [
    ['trackSingle', ids[0], 'Lead', {value: 2}],
    ['trackSingle', ids[0], 'PageView', {}, {eventID: 'local-test'}],
    ['init', ids[0], {em: 'test@example.invalid'}],
    ['track', 'PageView'], ['consent', 'revoke'], ['init', 'different-pixel']
  ];
  calls.forEach(a => {s.w.fbq.apply(null, a); assert.deepEqual(s.sent.at(-1), a);});
  vm.runInContext(source, s.context);
  assert.equal(s.scripts.length, 1);
  assert.equal(s.w.fbq, s.w._fbq);
  assert.equal(s.w.fbq.push, s.w.fbq);
  assert.equal(s.w.fbq.version, '2.0');
  console.log('PASS:', order, '— init único, PageView inicial único, chamadas posteriores intactas');
}
const late = setup();
// Falha inicial de biblioteca: fila existe até o GTM tentar carregá-la novamente.
late.gtm(); late.sdk();
assert.equal(late.sent.filter(a => a[0] === 'trackSingle').length, 2);
const foreign = () => {};
const preserved = setup(foreign);
assert.equal(preserved.w.fbq, foreign);
assert.equal(preserved.scripts.length, 0);
const nonempty = setup(); nonempty.sdk();
nonempty.w.fbq('trackSingle', ids[0], 'PageView', {content_name: 'other'});
nonempty.w.fbq('trackSingle', ids[0], 'PageView', {}, {eventID: 'other'});
assert.equal(nonempty.sent.filter(a => a[0] === 'trackSingle').length, 4);
nonempty.gtm();
assert.equal(nonempty.sent.filter(a => a[0] === 'trackSingle').length, 4);
console.log('PASS: falha de biblioteca, fbq preexistente e eventos com parâmetros preservados');
