/* Meta antecipada: PageView cedo; GTM v28 assume depois, sem repetir a visita inicial.
 * Compatibilidade limitada às chamadas vazias das tags Meta 5/34.
 * Não é deduplicação da Meta. Não suprime outros eventos nem visitas posteriores.
 * Configuração por página em window.__cmMetaCfg (gerada de rastreamento.json):
 *   envio_leve: PageView por requisição leve na abertura; SDK só na 1ª interação/5s.
 *   oferta: "#seletor" ou "texto:<trecho>" para o evento ViuOferta.
 */
(function (w, d) {
  if (w.fbq || w._fbq) return;
  var cfg = w.__cmMetaCfg || {};
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

  var sent = false;
  if (cfg.envio_leve) {
    try { sent = lightPageView(); } catch (e) { sent = false; }
  }
  // Reproduz a configuração pública existente: consent=true, sem matching adicional.
  fbq('consent', 'grant');
  ids.forEach(function (id) {
    fbq('init', id, {});
    fbq('set', 'agent', 'tmSimo-GTM-WebTemplate', id);
    // Com envio leve confirmado, o SDK não repete a visita; sem ele, segue o fluxo antigo.
    if (!sent) fbq('trackSingle', id, 'PageView', {});
    pendingInit[id] = true;
    pendingView[id] = true;
  });

  var injected = false;
  function loadSdk() {
    if (injected) return;
    injected = true;
    var script = d.createElement('script');
    script.async = true;
    script.src = 'https://connect.facebook.net/en_US/fbevents.js';
    var first = d.getElementsByTagName('script')[0];
    first.parentNode.insertBefore(script, first);
  }
  if (!sent) {
    loadSdk();
  } else {
    var go = function () {
      if (injected) return;
      if (w.requestIdleCallback) w.requestIdleCallback(loadSdk, {timeout: 1500});
      else w.setTimeout(loadSdk, 1);
    };
    ['scroll', 'mousemove', 'touchstart', 'click', 'keydown'].forEach(function (e) {
      w.addEventListener(e, go, {once: true, passive: true});
    });
    w.setTimeout(go, 5000);
  }

  function cookie(name) {
    var m = d.cookie.match(new RegExp('(?:^|; )' + name + '=([^;]*)'));
    return m ? decodeURIComponent(m[1]) : '';
  }
  // Mesmo domínio e índice do SDK: .contemmagia.com.br → "fb.2."; domínio simples → "fb.1.".
  function labels() {
    return /\.(com|net|org|gov|edu)\.[a-z]{2}$/.test(w.location.hostname) ? 3 : 2;
  }
  function setCookie(name, value) {
    var domain = w.location.hostname.split('.').slice(-labels()).join('.');
    d.cookie = name + '=' + value + ';max-age=7776000;path=/;domain=.' + domain + ';SameSite=Lax';
  }
  function lightPageView() {
    var now = Date.now();
    var fbp = cookie('_fbp');
    var index = labels() - 1;
    if (!/^fb\.\d\.\d+\.\d+$/.test(fbp)) {
      fbp = 'fb.' + index + '.' + now + '.' +
        String(Math.floor(Math.random() * 1e9)) + String(Math.floor(Math.random() * 1e9));
      setCookie('_fbp', fbp);
    }
    var fbc = cookie('_fbc');
    var click = (w.location.search.match(/[?&]fbclid=([^&#]*)/) || [])[1];
    if (click) {
      click = decodeURIComponent(click);
      if (fbc.split('.').slice(3).join('.') !== click) {
        fbc = 'fb.' + index + '.' + now + '.' + click;
        setCookie('_fbc', fbc);
      }
    }
    if (cookie('_fbp') !== fbp) return false;
    var ok = false;
    ids.forEach(function (id) {
      var p = [
        ['id', id], ['ev', 'PageView'], ['dl', w.location.href], ['rl', d.referrer],
        ['if', 'false'], ['ts', String(now)], ['sw', String(w.screen.width)],
        ['sh', String(w.screen.height)], ['ec', '0'], ['a', 'tmSimo-GTM-WebTemplate'],
        ['fbp', fbp], ['it', String(now)], ['coo', 'false']
      ];
      if (fbc) p.push(['fbc', fbc]);
      var q = p.map(function (x) { return x[0] + '=' + encodeURIComponent(x[1]); }).join('&');
      var url = 'https://www.facebook.com/tr/';
      if (url.length + q.length + 12 < 2000) {
        var img = new w.Image();
        img.src = url + '?' + q + '&rqm=GET';
        ok = true;
      } else if (w.navigator.sendBeacon) {
        ok = w.navigator.sendBeacon(url, new w.Blob([q + '&rqm=SB'],
          {type: 'application/x-www-form-urlencoded'})) || ok;
      }
    });
    return ok;
  }
})(window, document);

/* Engajamento para remarketing: uma vez por carregamento, aos pixels já iniciados. */
(function (w, d) {
  try {
    var cfg = w.__cmMetaCfg || {};
    var fired = {};
    var send = function (name) {
      if (fired[name] || !w.fbq) return;
      fired[name] = true;
      w.fbq('trackCustom', name);
    };
    // Leitura ativa: 30s com a aba visível e ao menos uma interação.
    var active = false, visibleMs = 0, last = Date.now();
    var ready = function () { if (active && visibleMs >= 30000) send('Leitura30s'); };
    var tick = function () {
      var now = Date.now();
      if (d.visibilityState !== 'hidden') visibleMs += now - last;
      last = now;
      if (visibleMs >= 30000) { ready(); return; }
      w.setTimeout(tick, 1000);
    };
    ['scroll', 'touchstart', 'click', 'keydown'].forEach(function (e) {
      w.addEventListener(e, function () { active = true; ready(); }, {once: true, passive: true});
    });
    w.setTimeout(tick, 1000);

    if (!cfg.oferta || !('IntersectionObserver' in w)) return;
    var findOffer = function () {
      if (cfg.oferta.indexOf('texto:') !== 0) return d.querySelector(cfg.oferta);
      var wanted = cfg.oferta.slice(6).replace(/\s+/g, ' ');
      var walker = d.createTreeWalker(d.body, 4);
      while (walker.nextNode()) {
        var el = walker.currentNode.parentElement;
        var text = walker.currentNode.nodeValue.replace(/[\s\u00a0]+/g, ' ');
        if (el && text.indexOf(wanted) !== -1 && el.getClientRects().length) return el;
      }
      return null;
    };
    var start = function () {
      var target = findOffer();
      if (!target) return;
      var timer = null;
      var observer = new w.IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting && !timer) {
            // 1s na tela evita contar quem só passou rolando.
            timer = w.setTimeout(function () { send('ViuOferta'); observer.disconnect(); }, 1000);
          } else if (!entry.isIntersecting && timer) {
            w.clearTimeout(timer);
            timer = null;
          }
        });
      });
      observer.observe(target);
    };
    if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', start, {once: true});
    else start();
  } catch (e) {}
})(window, document);
