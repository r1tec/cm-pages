# Plano — SEO das páginas Front1

Data: 19/10/2026. Pesquisas que sustentam o plano (com fontes):
`docs/seo/PESQUISA-SEO-2026-10-19.md` (estratégia, checklist, dados estruturados,
prazos) e `docs/seo/PESQUISA-MONITORAMENTO-2026-10-19.md` (painel e atribuição de venda).

Front1 = páginas de produto de entrada (R$ 39,90): `drb`, `bce`, `bco`, `bpa`,
`bpv`, `coe`, `gdp`, `mce`, `mpg` (+ `mpp`, parcelado). `fsa` tem o título
"Bundled Page" e entra na faxina de títulos.

## Situação em 19/10/2026

1. **O domínio está barrando o Google.** `robots.txt`, `sitemap.xml`, a home e as
   páginas que ainda moram no WordPress (`iat`, `t3x`, `6-edb`, `drb-vsl`) respondem
   **erro 500** ("Há um erro crítico no seu site"). Com `robots.txt` em 500 o Google
   para de rastrear o domínio nas primeiras 12 h e, se o site parecer fora do ar por
   30 dias, para de vez. As páginas estáticas (`/drb/`, `/bce/`…) respondem 200,
   mas o Google decide pelo `robots.txt` do domínio. **Nada de SEO rende antes disso.**
2. **Não há Search Console** conferido para o domínio (sem ele: sem sitemap enviado,
   sem pedido de indexação, sem dados para o painel).
3. **Títulos internos vazam para o Google**: "DRB – … – V3 – Contém Magia",
   "MPG – Magia Com Pombogira v2", "Bundled Page". Nenhuma página tinha tags de
   compartilhamento (`og:`) nem dados de produto.
4. **Venda orgânica fica invisível**: o script dos botões repassa os parâmetros da
   URL ao checkout; quem chega do Google não traz parâmetro, então a venda entra sem
   origem.

## O que já foi feito (build 1 — DRB, no ar)

Só o cabeçalho e o texto alternativo da foto; **nenhum texto visível mudou**.

- Título: **"Rezas e Benzimentos Antigos de Benzedeira: o Diário em PDF"** (58
  caracteres; abre com a frase que o Google mais sugere para este produto).
- Descrição (o "anúncio" que aparece no Google, escrita para dar curiosidade):
  "As rezas que as benzedeiras guardavam a sete chaves, contra mau-olhado,
  quebranto e inveja, para proteger a casa e abrir caminhos. Em PDF, para benzer
  você mesma." — usa só o que a página já promete.
- Tags de compartilhamento (WhatsApp/Facebook) com imagem 1200×630 nova
  (`drb/assets/og-drb.jpg`).
- Dados de produto (`Product` + `Offer`, R$ 39,90) — único tipo ainda útil para
  página de venda; sem avaliações marcadas (risco de punição) e sem FAQ marcado
  (o Google deixou de mostrar em 05/2026).
- Texto alternativo da foto do topo e correção do erro "Caderno de Rez**os**".
- Conferido no ar: título, 10 tags, dados de produto, imagem 200 e os 7 botões de
  compra continuam repassando os parâmetros de campanha.

Não mexi: os dois títulos principais (H1) da página — o Google aceita, e trocar
mudaria o visual; e a divergência **"59 rezas" no topo × "49 rezas" mais abaixo**,
que é texto aprovado (decidir qual vale).

## Como escolher as palavras (método que vira skill)

Fonte grátis e real: sugestões do Google (`scripts/palavras_chave.py "semente" …`),
"As pessoas também perguntam" e, depois de ligado, o Search Console.

Três camadas por produto:

| Camada | Para quê | Onde entra | DRB |
|---|---|---|---|
| **Compra** (quem já quer o produto) | ranquear a página de venda | título, descrição, H1 | "rezas e benzimentos antigos", "caderno/livro de rezas e benzimentos (pdf)", "rezas antigas de benzedeiras pdf", "curso de benzimento online", "como aprender a ser benzedeira" |
| **Curiosidade** (dor da persona) | gancho da descrição; tema de artigo | descrição; artigos | "reza contra mau olhado e inveja", "benzimento para criança", "reza para quebranto", "reza para abrir caminhos", "como se benzer sozinha", "benzer em casa" |
| **Marca** (já procuram o nome) | não perder quem já procura | título | DRB ainda sem; irmãs sim: "guia de pemba edu parmeggiani", "magia com exu edu parmeggiani", "guia de benzimento com ervas pdf", "benzimento animais livro" |

Regras: título 40–60 caracteres com a palavra de compra no começo; descrição até
~160 com o gancho de curiosidade e só promessas que a página já faz; nada de
prometer cura ou dinheiro (vira tema sensível para o Google); nunca repetir
palavras de forma artificial.

**Limite honesto:** a página de venda ranqueia para "compra" e "marca". As buscas
de curiosidade ("reza contra mau olhado") o Google entrega a artigos, não a
páginas de venda. Para captar essa massa é preciso conteúdo (build 6).

## Builds

Registro: `n:título@arquivos<dependências`.

```
0:destravar-rastreamento@raiz.py+config/raiz/+config/contemmagia-raiz.htaccess   FEITO 19/10
1:drb-cabecalho@drb/index.html+drb/assets/og-drb.jpg            FEITO 19/10
2:search-console@(fora: Google + Cloudflare DNS)<0
3:seo-no-pipeline@preparar.py+seo.py+<slug>/seo.json+tests<1    FEITO 19/10
4:skill-seo@.claude/skills/seo/+.claude/skills/preparar-pagina/<3   FEITO 19/10
5:front1-em-lote@bce,bco,bpa,bpv,coe,eba,fsa,gdp,mce,mpg,mpp/seo.json<3,4   FEITO 19/10
6:conteudo-informativo@(decisão do dono)<2,5
7:origem-na-pagina@seo.py (ORGANICO_JS)   FEITO 19/10
8:painel-coleta-gsc@raiz1-lovable: supabase/functions+migrations<2
9:painel-cwv-indexacao@raiz1-lovable<8
10:origem-no-pedido@raiz1-lovable checkout (financeiro, /esteira)<7
11:tela-seo@raiz1-lovable src/<8,9,10
```

### Feito em 19/10/2026 (builds 0, 3, 4, 5)
- **Raiz:** `raiz.py --publicar` sobe `robots.txt`, `sitemap.xml` (de
  `config/raiz/paginas.json`) e a home `inicio.html`, e instala o bloco
  `config/contemmagia-raiz.htaccess` antes do WordPress (desativado): `/` mostra
  a home e endereço inexistente responde 404. Backup do `.htaccess` original no
  servidor: `public_html/.htaccess.bk-cm-raiz`. Conferido: home, robots e sitemap
  200; páginas, redirecionamentos e eduparmeggiani.com iguais ao antes.
- **Pipeline:** `seo.py` aplica `<slug>/seo.json` no build (título, descrição,
  canonical, `og:`, JSON-LD `Product`) e recusa preço que a página não mostra.
- **Lote:** 10 páginas com `seo.json` e imagem `assets/og-<slug>.jpg`; corpo de
  cada página conferido idêntico ao que estava no ar. Corrigidas descrições
  trocadas (mce/mpg/mpp exibiam a do Guia de Pemba; bce/bpa a do Diário).
- **`coe`:** a versão no ar vinha de um `estatico.py` antigo. Investigado: a data
  diferente é do contador do evento ECM, que nem roda no `coe` (sem `data-cd`); a
  outra diferença eram animações de entrada congeladas. Republicado pelo pipeline;
  texto e links idênticos. Original guardado fora da área pública em
  `backup-cm-pages/coe-index-antes-seo-2026-10-19.html`.
- **`eba` e `fsa`** entraram no lote (preço = plano anual à vista: R$ 397 e R$ 1.297).
- **`ecm-26`** (evento de 10–11/10/2026, inscrições encerradas) saiu do sitemap e
  da home; a página continua no ar.
- **DRB "59 × 49":** o produto diz "49 rezas/benzimentos" quatro vezes; o "59" do
  topo veio errado do WordPress. Topo corrigido para 49 (prometer a mais gera
  reembolso e reclamação).
- **Venda orgânica rotulada (build 7, decidido e feito):** `seo.py` injeta o
  `ORGANICO_JS`: visita vinda de buscador sem `utm_*`/`gclid`/`fbclid` ganha
  `utm_source=<buscador>&utm_medium=organic` na URL, e os scripts de compra
  existentes repassam ao checkout. Escolhido UTM (e não parâmetro próprio) porque
  o checkout já recebe UTM dos anúncios e o GA4 classifica `medium=organic` como
  busca orgânica — nada muda no checkout. Provado em Chrome real nas páginas
  publicadas (Google, Bing, anúncio com UTM, fbclid, direto).
- **IndexNow:** `raiz.py --publicar` avisa Bing/Yandex/outros (chave em
  `config/raiz/indexnow-chave.txt`); primeira chamada aceita (202, 13 endereços).
- **Search Console já existe:** o DNS tem `google-site-verification=1Whep…` e a raiz
  tem `google35d534239d1ce1d6.html` (2022). A propriedade está em alguma conta
  Google da escola; não apagar nenhum dos dois. Falta só entrar nela, enviar
  `https://contemmagia.com.br/sitemap.xml` e liberar o acesso da conta de
  serviço do painel (build 8).

### 0 — Destravar o rastreamento (bloqueador; fora do cm-pages)
- **Hoje:** WordPress da raiz com erro crítico; `robots.txt` e sitemap em 500.
- **Depois:** `robots.txt` responde 200 com `Sitemap:` apontando para o sitemap
  das páginas estáticas; a home volta ou responde algo estável.
- **Caminho:** consertar o WordPress (plugin/tema que quebrou) **ou**, se o
  WordPress vai sair, subir um `robots.txt` físico e um `sitemap-paginas.xml` na
  raiz do servidor (o servidor entrega arquivo físico antes do WordPress).
- **Tela:** nada visível. **Efeitos:** o `robots.txt` vale para o domínio todo.
- **Custo:** baixo (1 build) se for o arquivo; depende da causa se for o WordPress.
- **Tem que fazer:** `curl /robots.txt` = 200 para Googlebot. **Não pode
  acontecer:** `Disallow` que bloqueie páginas de venda.

### 2 — Search Console (ação do dono, ~15 min)
Propriedade de domínio `contemmagia.com.br`, verificada por registro TXT no
Cloudflare (o assistente do Google faz sozinho; nunca apagar o TXT). Enviar o
sitemap e pedir indexação da `/drb/`. Detalhe: pesquisa SEO, seção 5.

### 3 — SEO dentro do pipeline
- **Hoje:** título, descrição e dados de produto ficam cravados no HTML de cada
  página; o preço do dado de produto pode ficar velho quando a oferta mudar.
- **Depois:** cada página tem `<slug>/seo.json` (título, descrição, imagem,
  nome do produto, preço). O `preparar.py` injeta as tags, confere tamanhos e o
  preço contra o texto da oferta (`rastreamento.json` → `oferta`, que é texto
  de exibição como `"texto:R$ 39,90"` — precisa ser lido, não é número) e gera
  `sitemap-paginas.xml` com todas as rotas.
- **Tela:** nada visível. **Efeitos:** mudar preço sem atualizar `seo.json`
  passa a falhar o build (de propósito). **Custo:** médio, 1 build.
- **Tem que fazer:** build da DRB igual ao de hoje no cabeçalho; teste com
  preço divergente falhando. **Não pode acontecer:** alterar corpo, checkout,
  rastreamento ou desempenho.

### 4 — Skill `seo`
Método acima (palavras → título/descrição → `seo.json` → conferência), chamada
pela `preparar-pagina` em toda página nova. **Custo:** baixo, 1 build.

### 5 — Front1 em lote
Pesquisa de palavras por produto + `seo.json` + publicação das 10 páginas.
**Tela:** nada visível. **Efeitos:** muda como as páginas aparecem no Google e
no WhatsApp. **Custo:** médio, 1–2 builds (pede "publica").

### 6 — Conteúdo informativo (decisão do dono)
Artigos que respondem às buscas de curiosidade e levam à página de venda
(ex.: "Reza contra mau-olhado: como benzer em casa" → `/drb`). A pesquisa mostra
que links internos têm a evidência mais sólida; "cluster" é boa prática sem
prova forte. **Decidir:** onde moram os artigos — rotas estáticas no cm-pages
(ex.: `/benzimento/reza-contra-mau-olhado`) ou um blog no WordPress — e quem
escreve com a voz e a experiência do Edu (o Google valoriza autoria real; texto
genérico de IA é sinal de baixa qualidade). **Custo:** alto e contínuo.

### 7 — Origem orgânica na página (cm-pages)
- **Hoje:** visita do Google chega ao checkout sem origem.
- **Depois:** o script dos botões identifica de onde a pessoa veio (Google,
  Bing, ChatGPT, direto), guarda primeira e última origem num cookie do domínio
  e leva ao checkout.
- **Decidir antes (dono):** marcar como `utm_source=google&utm_medium=organic`
  (padrão do GA4, mas o checkout passa a ver como "campanha") **ou** parâmetros
  próprios (`canal`, `lp`, `ref`) — a pesquisa recomenda os próprios.
- **Tela:** nada visível. **Efeitos:** link de checkout ganha parâmetros; mexe
  em rastreamento (passa por validação). A DRB tem script próprio de repasse,
  separado do `estatico.py` — os dois precisam mudar. **Custo:** médio, 1 build.

### 8–11 — Painel no raiz1-lovable (segundo momento, branch própria)
Conta de serviço do Google → função diária → tabelas dia × página × consulta
(guardar já: o Google só mantém 16 meses) → tela "SEO" com cliques, posição,
oportunidades, Core Web Vitals reais, status de indexação e vendas orgânicas por
página. APIs gratuitas. Origem no pedido (10) é checkout → fluxo financeiro com
validação. Arquitetura, limites e referências: pesquisa de monitoramento, seções
1–5.

## Prazos realistas
Mudança de título leva dias a semanas para aparecer; página nova costuma levar
semanas a meses; só ~1,7% das páginas novas chegam ao top 10 em um ano
(Ahrefs 2025). Marca e "compra" vêm primeiro; curiosidade só com conteúdo.

## Revisão por especialistas (19/10/2026, no ar)
Relatórios de SEO técnico, conteúdo e dados estruturados. Aplicado e publicado:
- `<meta charset>` no topo e fim do preload de fonte embutida (HTML 20–60 KB menor);
- ícone e logo da escola (`config/raiz/marca`), robots `max-image-preview:large` nas 12;
- `Product` com `sku`, `@id` da organização e garantia (`garantia_dias`, conferida no texto);
- rodapé "Outros guias" em todas as páginas (links internos; corrige #dc-root em 100%);
- alt de ~35 imagens; títulos de mpp (curso de pemba), mpg (Pomba Gira) e bpa (cachorro e gato);
- erros de digitação: bco "com Ervas"→"com Orixás", bpa "Aniamais", mpg "Guia do guia";
- home com texto, Edu, dados da empresa, `WebSite`/`Organization`/`Person` e og;
- `.htaccess`: www→sem www (301), restos do WP em 410, ecm-26 e ecm-26-v1 com noindex.
Não feito de propósito: BreadcrumbList e VideoObject (ganho ~0), preço riscado,
`priceValidUntil`, Merchant Center (política proíbe PDF e cursos).

## Pendências
- Search Console: sitemap enviado e processado (13 páginas) em 19/10/2026, conta
  operacoes@raiz1.com.br.
- Decisões do dono: número de alunos (12, 17, 35, 42 e 44 mil conforme a página);
  módulos 3–6 do mpp com o mesmo título; página Sobre/autor com fatos reais; links
  oficiais de Instagram/YouTube (entram no `sameAs`); guias informativos (build 6).
- Opcional: Bing Webmaster Tools importando do Search Console (~5 min, login do dono);
  alt das 3 imagens do fsa (exige mexer em `scripts/preparar-fsa.py`).
- Painel no raiz1-lovable: `docs/seo/MONITORAMENTO-SEO-RAIZ1.md` (o pedido já grava
  `url_utm_*`, então a venda orgânica já chega ao banco).
