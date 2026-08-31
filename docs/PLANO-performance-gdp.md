# Plano de performance — página `gdp` (mobile → ~97)

Auditoria feita sobre o HTML **realmente servido** (`python3 otimizar.py gdp`), renderizado no Chrome headless com emulação mobile (viewport 412×915, DPR 2.6) e conferido contra o site no ar. Todo número abaixo foi medido, com o comando ao lado.

Métricas de partida (Moto G, 4G lento): FCP 1,7s · LCP 3,1s · TBT 410ms · CLS 0 · SI 4,1s.

---

## Diagnóstico do LCP (a causa raiz dos 3,1s)

**O elemento LCP é a CAPA** — `gdp01.webp` — mas não como `<img>`, e sim como **imagem de fundo (`background-image`) de um DIV** (o container do topo, `elementor-element-9989bfa e-con-full`). Medido via PerformanceObserver `largest-contentful-paint`:

```
LCP url = assets/gdp01.webp   tag = DIV   size = 123.600 px²
```

O preload `as=image fetchpriority=high` está **certo e ajudando**: imagem de fundo em CSS só é descoberta depois que o CSS é lido, então o preload adianta o download. Não mexer nisso.

**Por que fecha só em 3,1s (e não em 88ms como no meu teste local sem freio):** o gargalo **não é a rede** (o Cloudflare já entrega em Brotli — confirmado `content-encoding: br` no ar) nem a imagem (22KB). O gargalo é o **CSS gigante embutido no `<head>`**:

- O `<head>` tem **196KB**, dos quais **194KB são CSS embutido** (2 blocos `<style>`), já minificado (só 1,5% de espaço em branco — não há ganho em minificar de novo).
- Esse CSS **trava a pintura**: o navegador precisa baixar o HTML, ler e montar os 194KB de CSS (≈1.500 regras) e casá-las contra os 534 nós da página ANTES de pintar o primeiro pixel. Num celular fraco isso custa centenas de ms de CPU. É o mesmo muro que segura o FCP (1,7s) e, logo atrás dele, o LCP.
- Confirmação de que o CSS é o peso: `gdp` servido = 258KB de HTML vs. `coe` (referência) = ~105KB. A diferença é quase toda esse CSS do Elementor.

**Consequência:** o maior ganho de LCP/FCP não é imagem nem fonte — é **enxugar o CSS embutido**.

### Quanto do CSS é lixo (medido)
Casando cada regra contra as classes/ids que **existem de fato** no DOM renderizado (uma regra cujas classes nunca aparecem no HTML **não pode pintar nada**, logo é seguro remover):

```
regras totais:            ~1.497   (191KB de corpo de regra)
regras que NÃO casam nada:   843   = 84KB  (44% do CSS)  ← removível sem risco visual
regras usadas:               654   = 107KB
```
(comando: match estático classes/ids do `rendered.html` × seletores do `<style>`; o rastreador nativo do Chrome confirmou a ordem de grandeza — reportou só 723 regras realmente acionadas.)

O lixo é o CSS de **blocos do WordPress/Gutenberg que a página nunca usa** (`.wp-block-*`, `.has-*-color`, `.is-layout-*`, `.alignwide/alignfull`, `.wp-elements-*`…) e **widgets do Elementor que esta página não tem**. O Elementor exporta isso sempre, use ou não.

---

## Tabela priorizada

| Ação | Métrica | Ganho estimado | Risco visual | Decisão do dono? | Como fazer |
|---|---|---|---|---|---|
| 1. Podar CSS morto do `<style>` embutido (44% / 84KB) | LCP, FCP, TBT, SI | Alto | Nenhum¹ | Não | No `otimizar.py`: após embutir, remover toda regra cujos seletores só citam classes/ids ausentes do DOM |
| 2. Tirar `fetchpriority="high"` do logo | LCP | Baixo | Nenhum | Não | Só a capa pode ser "high"; o logo disputa banda com o LCP |
| 3. Reduzir o arquivo do logo (668×256 → ~522×200) | LCP, SI | Baixo | Nenhum | Não | Logo é exibido a 261×100; está 2,5× maior que o necessário |
| 4. Cachear o HTML na borda do Cloudflare | (campo/TTFB) | Baixo-médio | Nenhum | Não (infra) | Hoje `cf-cache-status: DYNAMIC` (não cacheia). Criar Cache Rule p/ `*/gdp/*` cachear HTML |
| 5. Poster nos 4 vídeos | (estabilidade) | Muito baixo | Nenhum | Não | Vídeos já são `preload="none"` e estão a 9000px do topo — não atrapalham o carregamento |
| 6. Cortar peso do rastreio (GTM/GA4/Pixel/Clarity) | **TBT** | **Alto** | Nenhum | **SIM** | Ver bloco abaixo |

¹ Risco zero por construção: uma regra cujas classes não existem no HTML não estiliza nada; removê-la não muda um pixel. Fazer a poda contra o DOM **renderizado pelo Chrome** (não o HTML cru), para captar classes que o próprio Elementor injeta.

### O que já está certo (validei — não refazer)
- CSS e fontes **embutidos** no `<head>`: confirmado, 194KB inline, zero `<link>` de CSS externo travando.
- `@font-face` das 3 fontes embutido, `font-display: swap` correto; preload só de Montserrat + Nunito Sans; Roboto de propósito sem preload (é pouco usada e não trava). Correto.
- Preload da capa `as=image fetchpriority=high`: correto e mira o elemento LCP real.
- GTM adiado (`setTimeout 3s` + 1º toque): correto, igual ao `coe`.
- `.htaccess` **é gerado** pelo `otimizar.py** e vai no build (a observação de que páginas Elementor não recebem `.htaccess` está desatualizada). Cache correto: imagens/fontes 1 ano `immutable`, css/js 1 semana, html 10 min. Brotli/gzip ligado na origem e no Cloudflare.
- Imagens abaixo da dobra (`mockup`, `fatia1-4`) com `loading="lazy"` e `width`/`height` (CLS 0). Correto.
- Fontes já parecem **subsetadas em Latin** (Montserrat 38KB, Nunito 31KB, Roboto 43KB para faces variáveis 100–900 — tamanho típico de subset Latin). Subsetar mais exige `fonttools` (não instalado) e o ganho seria pequeno com risco de perder acento português. **Não vale a pena** — a suposição de "112KB subsetável" do briefing não se confirma.
- DOM: **534 nós, profundidade 13** — abaixo do limite de alerta do PageSpeed (~800). O "otimize o DOM" é ruído; achatar `div` do Elementor é risco alto e ganho ~zero. **Ignorar.**

---

## Faz agora — risco zero/baixo (sem tocar em rastreio)

Em ordem de impacto:

1. **Podar o CSS morto (ação 1).** É o único item que move LCP/FCP/SI de verdade. No `otimizar.py`, depois de `_embutir_css_local`: renderizar a página uma vez (headless, como fiz) para colher todas as classes/ids reais, e apagar do bloco `<style>` toda regra cujos seletores só mencionam classes/ids ausentes. Roda para as 5 páginas. Corta ~84KB (44%) do `<head>`.
2. **Logo (ações 2 e 3).** Tirar `fetchpriority="high"` do `<img>` do logo e regravar o `logo.webp` a ~522×200. Editável na fonte (`gdp/index.html` + arquivo) ou como passo no build.
3. **Cache de HTML no Cloudflare (ação 4).** Uma Cache Rule para as slugs. Melhora TTFB de campo; não muda o número de laboratório do PageSpeed, mas ajuda usuário real.

**Chega a 97 só com isto?** Não. Vai levar **LCP, FCP e Speed Index para o verde** e CLS já é 0 — provável **~92–95**. O teto é o **TBT (410ms)**, que vem quase todo do rastreio disparado aos 3s. Sem mexer nele, não passa de ~95.

---

## Precisa decisão do dono (rastreio) — é o que falta para os últimos pontos

O TBT de 410ms e as "7 tarefas longas" são o **JS de terceiros**: GA4/gtag (164KB), gtm.js (153KB), gtag/destination (141KB), Facebook `fbevents` (105KB) e Clarity. Já estão adiados para 3s — tecnicamente já fizemos o possível **sem cortar tag**. Para o TBT cair a ~200ms (necessário para ~97), o dono precisa escolher:

- **Cortar tags** que talvez não sejam essenciais: Facebook Pixel (105KB + é o "JS legado" que o PageSpeed aponta) e/ou Microsoft Clarity. Cada um que sai tira tarefa longa da thread.
- **Ou** mover o GTM para **server-side** (o navegador para de executar o peso).
- **Não** adianta `preconnect` para Google/Facebook: como as tags só disparam aos 3s, pré-conectar cedo só rouba banda do LCP. O `preconnect` aqui **atrapalharia** — não fazer.
- Cache curto dos arquivos do Facebook/Clarity: é servido por eles, fora do nosso controle. Ignorar.

**Veredito honesto:** bloco de risco baixo → ~92–95 (LCP/FCP/SI verdes). Os pontos que faltam para 97 estão **presos no TBT do rastreio** e são **decisão do dono** (tirar Pixel/Clarity ou ir para server-side GTM). Isso vale para as 5 páginas, não só a `gdp`.
