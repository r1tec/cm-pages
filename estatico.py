#!/usr/bin/env python3
# Transforma a página montada por JavaScript numa página ESTÁTICA (pronta),
# como as do WordPress: HTML de verdade que aparece na hora, sem esperar React.
#
# Recebe o HTML já renderizado (headless) e devolve um index.html enxuto:
#   - remove TODO o JavaScript de montagem (React, motor do bundler)
#   - mantém só: o pixel (GTM) e o pedacinho do botão de compra
#   - pré-carrega a imagem principal (capa) para o LCP ser instantâneo
#
# Uso:  python3 estatico.py <rendered.html> <saida/index.html> [hero_uuid]

import sys, re
from rastreamento import GTM_ID, GTM_HEAD
GTM_BODY = (
    '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM_ID + '"'
    ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
)
# Favicon embutido (quadradinho na cor da marca). Sem arquivo externo: evita o
# 404 de /favicon.ico que o navegador pede sozinho e que derruba a nota de
# "Boas práticas" (erro no console).
FAVICON_LINK = (
    '<link rel="icon" href="data:image/svg+xml,'
    "%3Csvg%20xmlns='http://www.w3.org/2000/svg'%20viewBox='0%200%2032%2032'%3E"
    "%3Crect%20width='32'%20height='32'%20rx='6'%20fill='%23C25A1C'/%3E%3C/svg%3E\">\n"
)
CHECKOUT_JS = """<script>
(function(){
  var H='pay.contemmagia.com.br';
  function withUtms(url){try{var u=new URL(url,location.href);if(u.hostname.indexOf(H)===-1)return null;
    new URLSearchParams(location.search).forEach(function(v,k){if(!u.searchParams.has(k))u.searchParams.set(k,v)});
    return u.toString()}catch(e){return null}}
  function patch(){document.querySelectorAll('a[href*="'+H+'"]').forEach(function(a){
    a.setAttribute('target','_blank');a.setAttribute('rel','noopener');
    var n=withUtms(a.getAttribute('href'));if(n)a.setAttribute('href',n)})}
  if(document.readyState!='loading')patch();else document.addEventListener('DOMContentLoaded',patch);
  document.addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');
    if(!a||!a.href||a.href.indexOf(H)===-1)return;var n=withUtms(a.getAttribute('href')||a.href);
    if(!n)return;e.preventDefault();window.open(n,'_blank','noopener')},true);
})();
</script>
"""

# Hover nos botões de compra (só CSS, custo zero) + animação de entrada leve.
# A animação só "esconde" elementos quando o JS confirma (html.js): sem JS, tudo
# aparece normal. Só transform/opacidade (roda na GPU, não causa pulo de layout).
INTERACOES_CSS = """<style>
a[href*="pay.contemmagia.com.br"]{transition:filter .18s ease,transform .18s ease,box-shadow .18s ease}
a[href*="pay.contemmagia.com.br"]:hover{filter:brightness(1.1);transform:translateY(-2px);box-shadow:0 10px 24px rgba(0,0,0,.28)}
a[href*="pay.contemmagia.com.br"]:active{transform:translateY(0);filter:brightness(.96)}
html.js [data-anim]{opacity:0;transform:translateY(34px) scale(.98);will-change:opacity,transform}
html.js [data-anim].in{opacity:1;transform:none;transition:opacity 1.05s ease,transform 1.05s cubic-bezier(.2,.75,.2,1)}
/* Primeira dobra: entra ao carregar SÓ por movimento (opacidade fica 1 -> FCP/LCP intactos) */
html.js [data-hero]{animation:heroIn .85s cubic-bezier(.2,.75,.2,1) both}
@keyframes heroIn{from{transform:translateY(34px)}to{transform:none}}
@media(prefers-reduced-motion:reduce){html.js [data-anim],html.js [data-hero]{opacity:1;transform:none;animation:none;transition:none}}
</style>
"""
ANIM_JS = """<script>
document.documentElement.className+=' js';
document.addEventListener('DOMContentLoaded',function(){
  var els=document.querySelectorAll('[data-anim]');
  if(!('IntersectionObserver' in window)){els.forEach(function(e){e.classList.add('in')});return;}
  var io=new IntersectionObserver(function(entries){entries.forEach(function(e){
    if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}})},
    {rootMargin:'0px 0px -8% 0px'});
  els.forEach(function(e){io.observe(e)});
});
</script>
"""

# LIVE_JS: mantém a página do evento ECM viva no navegador (o pré-montador tira o
# React, então sem isto o contador congela). Só age se a página tiver as "alças"
# data-cd/data-encerrado — em qualquer outra página o script sai na primeira linha.
# Contador anda a cada segundo, vira de janela sozinho, fecha sozinho após a última
# data, e as barras buscam o número de ingressos ao vivo (endpoint público, só números).
LIVE_JS = """<script>
(function(){
  var root=document.querySelector('[data-encerrado]');
  var cd=document.querySelector('[data-cd]');
  if(!root||!cd)return;
  var ISO=['2026-09-10T23:59:59-03:00','2026-09-17T23:59:59-03:00','2026-09-24T23:59:59-03:00','2026-10-01T23:59:59-03:00','2026-10-08T23:59:59-03:00'];
  var DM=['10/09','17/09','24/09','01/10','08/10'];
  var PROX=['11/09','18/09','25/09','02/10',null];
  var TETOS=[130,140,150,160,170], RAIZ_TOTAL=30;
  var marcos=ISO.map(function(d){return new Date(d).getTime();});
  var ultimo=marcos[marcos.length-1], curIdx=0;
  function pad(n){return (n<10?'0':'')+n;}
  function set(sel,txt){var l=document.querySelectorAll(sel);for(var i=0;i<l.length;i++)l[i].textContent=txt;}
  function tick(){
    var now=Date.now();
    var encerrado=now>ultimo;
    var idx=-1;for(var i=0;i<marcos.length;i++){if(marcos[i]>now){idx=i;break;}}
    if(idx<0)idx=marcos.length-1;
    curIdx=idx;
    var alvo=marcos[idx], ehUlt=idx===marcos.length-1;
    var diff=Math.max(0,alvo-now), H=3600000, D=86400000;
    set('[data-cd=\\"dias\\"]',pad(Math.floor(diff/D)));
    set('[data-cd=\\"horas\\"]',pad(Math.floor((diff%D)/H)));
    set('[data-cd=\\"min\\"]',pad(Math.floor((diff%H)/60000)));
    set('[data-cd=\\"seg\\"]',pad(Math.floor((diff%60000)/1000)));
    set('[data-frase]', ehUlt ? ('As inscrições se encerram em '+DM[idx]+'.') : ('A partir de '+PROX[idx]+' o valor do ingresso aumenta.'));
    set('[data-fixdate]',DM[idx]);
    root.setAttribute('data-encerrado', encerrado?'1':'0');
  }
  tick(); setInterval(tick,1000);
  var A='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Iml1cWVkam5zbHptZ2hib2tteG92Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDA2ODA5NDYsImV4cCI6MjA1NjI1Njk0Nn0.hroTq_clsVfn8x3z06FVWVoVTXeVSeahfiidadS7Be0';
  fetch('https://iuqedjnslzmghbokmxov.supabase.co/functions/v1/get-ecm-ingressos-public',{headers:{apikey:A,Authorization:'Bearer '+A}})
    .then(function(r){return r.ok?r.json():null;})
    .then(function(d){
      if(!d||typeof d.vendidos!=='number')return;
      var teto=TETOS[curIdx];
      var semPct=Math.min(100,Math.round(d.vendidos/teto*100));
      var raizRest=Math.max(0,RAIZ_TOTAL-d.raizPagos);
      var raizPct=Math.round((RAIZ_TOTAL-raizRest)/RAIZ_TOTAL*100);
      var f;
      f=document.querySelectorAll('[data-fill=\\"sem\\"]');for(var i=0;i<f.length;i++)f[i].style.width=semPct+'%';
      f=document.querySelectorAll('[data-fill=\\"raiz\\"]');for(var j=0;j<f.length;j++)f[j].style.width=raizPct+'%';
      set('[data-sempct]',semPct+'%');
      set('[data-semfrase]','Seja rápido. '+semPct+'% das vagas já foram preenchidas.');
      set('[data-raizlabel]','Restam '+raizRest);
    }).catch(function(){});
})();
</script>
"""

def avisar_scripts_proprios(rendered_html):
    """Avisa (stderr) se a página RENDERIZADA (a que vira foto estática) tem script
    feito à mão — código que a etapa de estatizar vai remover e que, por isso, NÃO
    vai funcionar no ar (o publicar tira o React). Se precisa de algo vivo (contador,
    dado ao vivo), o caminho é injetar no padrão LIVE_JS aqui no estatico.py.

    Checa o RENDERIZADO (não o HTML-fonte, que é um pacote com <script> soltos dentro
    de textos e daria falso alarme). No renderizado, o que é do próprio bundler tem
    assinatura conhecida e é ignorado: motor DCLogic (`type="text/x-dc"`), scripts com
    `src` e sem corpo (bundler/blob), e o mapa de recursos (`window.__resources`)."""
    proprios = 0
    for m in re.finditer(r'<script\b([^>]*)>([\s\S]*?)</script>', rendered_html, flags=re.I):
        attrs, corpo = m.group(1).lower(), m.group(2).strip()
        if 'text/x-dc' in attrs:
            continue  # motor DCLogic (esperado)
        if re.search(r'\bsrc\s*=', attrs) and not corpo:
            continue  # bundler externo/blob com src e sem corpo (esperado)
        if corpo.startswith('window.__resources') or corpo.startswith('window.__bundler'):
            continue  # runtime do bundler (esperado)
        proprios += 1
    if proprios:
        print(f"  AVISO: {proprios} script(s) proprio(s) desta pagina serao REMOVIDOS pela versao "
              f"estatica (o publicar tira o React). Se precisa funcionar no ar (contador, dado ao "
              f"vivo, algo que muda sozinho), injete no padrao LIVE_JS dentro do estatico.py -- ver "
              f"a skill publicar. Do jeito atual essa parte vai CONGELADA pro visitante.",
              file=sys.stderr)
    return proprios


def _animar_secoes_de_texto(h):
    """Marca com data-anim o CONTEÚDO das <section> de texto — não a própria section.
    Anima o primeiro <div> interno (título + texto juntos), deixando a section e o
    FUNDO dela parados. Assim a entrada desliza/aparece só o conteúdo, sem revelar
    a cor do bloco de trás nem uma faixa nas bordas (o scale encolhia a section).
    Pula a primeira (capa, já tem data-hero) e as que já têm <article>/<figure>
    dentro (esses animam item a item). Evita bloco-dentro-de-bloco (piscar duplo)."""
    starts = [m.start() for m in re.finditer(r'<section\b', h, flags=re.I)]
    marcar = []  # posições onde inserir data-anim (no 1º <div> de cada section)
    for i, s in enumerate(starts):
        e = starts[i + 1] if i + 1 < len(starts) else len(h)
        trecho = h[s:e]
        if i == 0:
            continue  # capa (já tem data-hero)
        if re.search(r'<(article|figure)\b', trecho, flags=re.I):
            continue  # já anima por dentro
        # acha o primeiro <div dentro desta section (o container do conteúdo)
        m = re.search(r'<div\b', trecho, flags=re.I)
        if not m:
            continue  # sem container interno: não anima (não escondemos a section)
        marcar.append(s + m.start())
    for s in reversed(marcar):        # de trás pra frente: não desloca os anteriores
        h = h[:s + 4] + ' data-anim' + h[s + 4:]   # logo após "<div"
    return h

def staticize(h, hero=None):
    # 0) Acessibilidade:
    #    a) idioma da página (leitores de tela e tradução) — <html lang="pt-BR">
    if re.search(r'<html\b[^>]*\blang=', h, flags=re.I) is None:
        h = re.sub(r'<html\b', '<html lang="pt-BR"', h, count=1, flags=re.I)
    #    b) marca o container principal como "main" (ponto de referência da página)
    if 'role="main"' not in h:
        h = re.sub(r'(<div\s+id="dc-root")', r'\1 role="main"', h, count=1, flags=re.I)
    #    c) charset como PRIMEIRO item do <head> + favicon embutido.
    #       O runtime do Claude Design injeta um <style> no topo do <head> e empurra
    #       o <meta charset> pra depois dos 1024 primeiros bytes — o Lighthouse
    #       reprova ("charset tarde demais"). Tiramos o charset de onde estiver e
    #       recolocamos colado no <head>, com o favicon logo em seguida.
    h = re.sub(r'<meta[^>]*charset=[^>]*>', '', h, flags=re.I)
    h = re.sub(r'(<head\b[^>]*>)', r'\1<meta charset="utf-8">\n' + FAVICON_LINK,
               h, count=1, flags=re.I)
    #    d) preload das fontes locais (Cera Pro etc.) no topo do <head>. Sem isso, a
    #       primeira pintura (FCP) espera a fonte chegar pra trocar; com o preload, a
    #       fonte entra na primeira rajada de download e o texto aparece bem antes.
    woffs = []
    for face in re.finditer(r'@font-face\s*\{[^}]*\}', h, flags=re.I):
        rule = face.group()
        # Extensões permanecem disponíveis para acentos especiais, mas não devem
        # competir com a capa no preload. O browser usa unicode-range sob demanda.
        ranges = re.search(r'unicode-range\s*:\s*([^;}]+)', rule, re.I)
        if ranges and not re.search(r'U\+0{1,4}-', ranges[1], re.I):
            continue
        m = re.search(r'url\(["\']?(assets/[^"\')]+\.woff2?)["\']?\)', rule, re.I)
        if m and m.group(1) not in woffs:
            woffs.append(m.group(1))
    if woffs:
        font_preload = "".join(
            '<link rel="preload" as="font" type="font/'
            + ("woff2" if u.lower().endswith("woff2") else "woff")
            + f'" crossorigin href="{u}">\n' for u in woffs)
        h = re.sub(r'(<link rel="icon"[^>]*>\n)', r'\1' + font_preload, h, count=1, flags=re.I)

    # 0) antes de remover os scripts, avisa se algum é código próprio (feito à mão)
    #    que a foto estática vai jogar fora sem funcionar no ar.
    avisar_scripts_proprios(h)
    # 1) remove TODO <script> (motor de montagem, pixels injetados em runtime, blobs)
    h = re.sub(r'<script[\s\S]*?</script>', '', h, flags=re.I)
    # 2) remove <link> de Google Fonts (as fontes já são locais em assets/)
    h = re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)\.com[^>]*>', '', h, flags=re.I)
    # 3) remove <noscript> antigos (vamos recolocar o do GTM)
    h = re.sub(r'<noscript>[\s\S]*?</noscript>', '', h, flags=re.I)

    # 4) cabeça: preload da capa (LCP) + GTM
    #    (sem preconnect ao pixel: ele carrega adiado, então preconnect no início é desperdício)
    head_inject = ""
    if hero:
        head_inject += (
            f'<link rel="preload" as="image" href="assets/{hero}.webp" fetchpriority="high">\n'
        )
    head_inject += INTERACOES_CSS + GTM_HEAD
    h = re.sub(r'</head>', head_inject + '</head>', h, count=1, flags=re.I)

    # 4b) animação de entrada só nos cartões (article) e depoimentos (figure) —
    #     estão abaixo da primeira tela. NÃO anima <section> (a capa/título ficam
    #     numa section, e escondê-la atrasaria o FCP/LCP).
    h = re.sub(r'(<(?:article|figure)\b)(?![^>]*data-anim)',
               r'\1 data-anim', h, flags=re.I)
    # 4c) primeira dobra: marca a primeira <section> (capa/título) p/ deslizar ao
    #     carregar. Só transform (a opacidade fica 1), então FCP/LCP não mudam.
    h = re.sub(r'(<section\b)', r'\1 data-hero', h, count=1, flags=re.I)
    # 4d) seções de TEXTO (sem cartões/depoimentos dentro) também animam, como um
    #     bloco (título + texto juntos). Pula a 1ª (capa) e as que já têm article/
    #     figure — assim nunca anima um bloco dentro de outro.
    h = _animar_secoes_de_texto(h)

    # 5) marca a capa como prioridade alta (LCP) e desliga lazy nela
    if hero:
        def boost(m):
            tag = m.group(0)
            if hero in tag:
                tag = tag.replace(' loading="lazy"', '')
                if 'fetchpriority' not in tag:
                    tag = tag[:-1] + ' fetchpriority="high">'
            return tag
        h = re.sub(r'<img[^>]*>', boost, h, flags=re.I)

    # 6) corpo: GTM noscript logo após <body>, e o script do checkout antes de </body>
    h = re.sub(r'(<body[^>]*>)', r'\1\n' + GTM_BODY, h, count=1, flags=re.I)
    h = re.sub(r'</body>', CHECKOUT_JS + ANIM_JS + LIVE_JS + '</body>', h, count=1, flags=re.I)
    return h


def detect_hero(rendered_html):
    """Escolhe a imagem principal (maior área) para pré-carregar (LCP)."""
    best_uuid, best_area = None, 0
    for m in re.finditer(r'<img[^>]*>', rendered_html, re.I):
        tag = m.group(0)
        src = re.search(r'src="assets/([0-9a-f-]{16,})\.\w+"', tag)
        if not src:
            continue
        w = re.search(r'\bwidth="(\d+)"', tag)
        ht = re.search(r'\bheight="(\d+)"', tag)
        area = (int(w.group(1)) if w else 0) * (int(ht.group(1)) if ht else 0)
        if area > best_area:
            best_area, best_uuid = area, src.group(1)
    return best_uuid


def main():
    src, out = sys.argv[1], sys.argv[2]
    h = open(src, encoding="utf-8").read()
    hero = sys.argv[3] if len(sys.argv) > 3 else detect_hero(h)
    result = staticize(h, hero)
    open(out, "w", encoding="utf-8").write(result)
    print(f"  estático: {len(result)//1024}KB (capa: {hero})")

if __name__ == "__main__":
    main()
