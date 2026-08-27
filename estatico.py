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

GTM_ID = "GTM-P629X98"

GTM_HEAD = (
    "<!-- Google Tag Manager (carregado após a página aparecer, p/ não travar a abertura) -->\n"
    "<script>(function(){var loaded=false;function load(){if(loaded)return;loaded=true;"
    "(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});"
    "var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';"
    "j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
    "f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','" + GTM_ID + "');}"
    "['scroll','mousemove','touchstart','click','keydown'].forEach(function(e){"
    "window.addEventListener(e,load,{once:true,passive:true})});"
    "setTimeout(load,3000);})();</script>\n"
    "<!-- End Google Tag Manager -->\n"
)
GTM_BODY = (
    '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM_ID + '"'
    ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
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
html.js [data-anim]{opacity:0;transform:translateY(30px) scale(.985);will-change:opacity,transform}
html.js [data-anim].in{opacity:1;transform:none;transition:opacity .6s ease,transform .75s cubic-bezier(.2,.75,.2,1)}
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

def staticize(h, hero=None):
    # 0) Acessibilidade:
    #    a) idioma da página (leitores de tela e tradução) — <html lang="pt-BR">
    if re.search(r'<html\b[^>]*\blang=', h, flags=re.I) is None:
        h = re.sub(r'<html\b', '<html lang="pt-BR"', h, count=1, flags=re.I)
    #    b) marca o container principal como "main" (ponto de referência da página)
    if 'role="main"' not in h:
        h = re.sub(r'(<div\s+id="dc-root")', r'\1 role="main"', h, count=1, flags=re.I)

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
    h = re.sub(r'</body>', CHECKOUT_JS + ANIM_JS + '</body>', h, count=1, flags=re.I)
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
