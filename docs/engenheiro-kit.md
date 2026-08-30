# Kit do engenheiro de carregamento (por slug)

Leia junto com `docs/receita-paginas.md` (a receita) e `README.md` (o pipeline).
Este kit traz o que já foi descoberto do terreno — não redescubra.

## Fatos do pipeline (importante)
- `otimizar.py`, para uma página que **não é do Claude Design** (sem
  `<script type="__bundler/manifest">`), **só copia a pasta como está**. Ele
  NÃO externaliza imagem, NÃO injeta pixel, NÃO adia script, NÃO cria `.htaccess`.
  → Portanto **a pasta `<slug>/` já tem que nascer otimizada e pronta**:
  `index.html` enxuto + `assets/` com imagens/fontes em arquivos próprios +
  `.htaccess` de cache/compressão (modelo abaixo).
- `verificar.py` só avisa (peso de imagem, contraste) — não bloqueia.
- `publicar.sh <slug>` faz: otimizar (copia) → verificar → FTP → limpa cache CF.
- Ferramentas presentes: Chrome, `cwebp`, `lftp`, credenciais no `.env`.

## Originais
`https://eduparmeggiani.com/<slug>/` (com barra final; sem barra dá 301).
Baixe UMA vez para o scratchpad, trabalhe do arquivo. Processe o HTML pesado
**no sandbox (ctx_execute)**, traga só o extrato — nunca cole o bruto no contexto.

## `.htaccess` que a pasta deve conter
```
<IfModule mod_deflate.c>
  AddOutputFilterByType DEFLATE text/html text/css application/javascript application/json image/svg+xml
</IfModule>
<IfModule mod_headers.c>
  <FilesMatch "\.(webp|png|jpe?g|gif|avif|woff2?|svg)$">
    Header set Cache-Control "public, max-age=31536000, immutable"
  </FilesMatch>
  <FilesMatch "\.html$">
    Header set Cache-Control "public, max-age=600"
  </FilesMatch>
</IfModule>
```

## Pixel do próprio original, ADIADO (carrega após a página aparecer)
Extraia o pixel do original (Facebook `fbq` e/ou Google `gtag`/GTM — ID + snippet)
e inclua no `index.html` adiado, no molde abaixo (troca o miolo pelo snippet real):
```html
<script>(function(){var l=false;function go(){if(l)return;l=true;
/* AQUI: o snippet real do pixel do original (fbq init+PageView, ou gtm.js, ou gtag) */
}
['scroll','mousemove','touchstart','click','keydown'].forEach(function(e){
 addEventListener(e,go,{once:true,passive:true})});setTimeout(go,3000);})();</script>
```

## Script de slug/UTM (checkout) — porte do coe, apontando para o host DESTA página
Use o host de checkout **do próprio original** (não force pay.contemmagia):
```html
<script>(function(){var H='HOST_DO_CHECKOUT_DESTA_PAGINA';
 function u(url){try{var x=new URL(url,location.href);if(x.hostname.indexOf(H)===-1)return null;
  new URLSearchParams(location.search).forEach(function(v,k){if(!x.searchParams.has(k))x.searchParams.set(k,v)});
  return x.toString()}catch(e){return null}}
 function p(){document.querySelectorAll('a[href*="'+H+'"]').forEach(function(a){
  a.setAttribute('target','_blank');a.setAttribute('rel','noopener');
  var n=u(a.getAttribute('href'));if(n)a.setAttribute('href',n)})}
 if(document.readyState!='loading')p();else addEventListener('DOMContentLoaded',p);
 addEventListener('click',function(e){var a=e.target.closest&&e.target.closest('a');
  if(!a||!a.href||a.href.indexOf(H)===-1)return;var n=u(a.getAttribute('href')||a.href);
  if(!n)return;e.preventDefault();open(n,'_blank','noopener')},true);})();</script>
```

## PageSpeed (sem chave, JSON processado no sandbox)
`https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<URL>&strategy=mobile&category=PERFORMANCE&category=ACCESSIBILITY&category=BEST_PRACTICES&category=SEO`
(e `strategy=desktop`). Extraia só as 4 notas ×100. Se alguma <97, otimize sem
tocar no layout (reduzir imagem, contraste, atributos a11y, meta/SEO, adiar/dividir
script), republique e remeça. Repita até o teto viável.

## Checklist de otimização (já nasça com tudo isto — validado no bce)
- `<html lang="pt-BR">` (não en-US).
- `role="main"` no container raiz do conteúdo (ex.: no `<div data-elementor-type="wp-page" ...>`).
- Emojis: se o original usa `<img class="emoji" ... alt="X">` do CDN s.w.org, troque pelo
  caractere unicode do próprio alt (tira requisição de terceiro + corrige unsized-images).
- `<video>`: use `preload="none"` (corta megabytes de metadata; vídeos remotos ficam remotos).
- Imagem de topo (LCP): `<link rel="preload" as="image" href="assets/<capa>.webp" fetchpriority="high">`
  no head, e `fetchpriority="high"` sem `loading="lazy"` na tag dela.
- Toda `<img>` com `width` e `height` explícitos (evita CLS).
- `.htaccess` com cache: imagens/fontes `immutable 1 ano`, **css/js `max-age=604800`**, html 600s.
- **Contraste:** o plano permite ajustar contraste reprovado, MAS quando o tom reprovado é a
  COR DA MARCA (verdes) usada em botão de compra e no mesmo tom sobre fundo claro E escuro,
  repintar quebra fidelidade — nesse caso MANTENHA a cor do original e anote como trava. Só
  ajuste contraste quando dá pra escurecer sem virar "outra cor" perceptível.
- MEÇA em `https://contemmagia.com.br/<slug>/` COM BARRA FINAL (sem barra = 301, -1s de perf).
- **CUIDADO caminho relativo do CSS:** se `styles.css` fica em `<slug>/assets/`, os `url()`
  dentro dele resolvem RELATIVO a `assets/`. Então a capa é `url(diario.webp)`, NUNCA
  `url(assets/diario.webp)` (isso vira `assets/assets/` e quebra o LCP). No `index.html` (que
  fica em `<slug>/`) o certo é `assets/diario.webp`. Bug real que afundou o LCP do drb (8.5s→2.8s).

## Tetos estruturais conhecidos (iguais nas 5, anote como trava, não pare)
- **best-practices mobile ~77:** cookies de terceiro do GTM (o pixel exigido). Insuperável mantendo o pixel.
- **acessibilidade ~94:** contraste dos verdes da marca do próprio original (preservado por fidelidade).
- **perf mobile ~78-85:** CSS do Elementor (render-blocking, ~200KB) + JS do GTM (exigido). Desktop fica ~99.

## Regra de ouro
Fidelidade é lei: mesmo texto, mesmas imagens, mesmos vídeos, mesmo link de compra,
mesmas cores/fontes/espaçamentos, mesma ordem de seções, os efeitos da própria página.
Performance nunca justifica desvio visual. Não parar por nada: travou → consulta
subagente sênior; insuperável → anota no relatório e segue.
