/* Piloto DRB: PageView cedo; GTM v28 assume depois, sem repetir a visita inicial.
 * Compatibilidade limitada às chamadas vazias das tags Meta 5/34.
 * Não é deduplicação da Meta. Não suprime outros eventos nem visitas posteriores.
 */
(function (w, d) {
  if (w.fbq || w._fbq) return;
  var ids = ['197461362094441', '884049927923756'];
  var pendingInit = {}, pendingView = {};
  function empty(value) {
    if (value == null) return true;
    if (typeof value !== 'object' || Array.isArray(value)) return false;
    return Object.keys(value).length === 0;
  }
  function fbq() {
    var a = arguments, id = String(a[1]);
    if (a[0] === 'init' && pendingInit[id] && a.length <= 3 && empty(a[2])) {
      delete pendingInit[id];
      return;
    }
    if (a[0] === 'trackSingle' && a[2] === 'PageView' && pendingView[id] &&
        a.length <= 4 && empty(a[3])) {
      delete pendingView[id];
      return;
    }
    if (fbq.callMethod) return fbq.callMethod.apply(fbq, a);
    fbq.queue.push(a);
  }
  w.fbq = w._fbq = fbq;
  fbq.push = fbq;
  fbq.loaded = true;
  fbq.version = '2.0';
  fbq.queue = [];
  fbq.cmEarlyPageView = true;
  // Reproduz a configuração pública existente: consent=true, sem matching adicional.
  fbq('consent', 'grant');
  ids.forEach(function (id) {
    fbq('init', id, {});
    fbq('set', 'agent', 'tmSimo-GTM-WebTemplate', id);
    fbq('trackSingle', id, 'PageView', {});
    pendingInit[id] = true;
    pendingView[id] = true;
  });
  var script = d.createElement('script');
  script.async = true;
  script.src = 'https://connect.facebook.net/en_US/fbevents.js';
  var first = d.getElementsByTagName('script')[0];
  first.parentNode.insertBefore(script, first);
})(window, document);
