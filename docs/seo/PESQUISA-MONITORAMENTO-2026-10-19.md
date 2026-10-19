# Pesquisa — painel de SEO e vendas da busca orgânica

Data: 2026-10-19. Somente leitura (web + 1 olhada no `estatico.py` do cm-pages).

## Resumo

- O padrão de mercado é simples: **conta de serviço Google → função agendada diária → tabela por dia × página × consulta no Postgres → painel**. As APIs são gratuitas; o custo é de construção (cerca de 5 builds, complexidade média).
- O Google só guarda 16 meses e as consultas raras vêm anonimizadas. Por isso é preciso **guardar o histórico já** e ter **duas tabelas** (totais por página, mais completos; e página × consulta, com lacunas).
- Venda orgânica não aparece sozinha: o Google não informa a palavra buscada. O caminho validado é **classificar o `document.referrer` na página de venda, guardar a origem (primeiro e último toque) e repassá-la ao checkout**, que grava no pedido. O cruzamento com o Search Console é feito **por página de entrada e dia**, nunca por palavra.
- Hoje o script do cm-pages (`estatico.py`, `CHECKOUT_JS`) só repassa os parâmetros da URL atual. Ele não lê o referrer e não guarda nada entre páginas. Visita orgânica (sem UTM) chega ao checkout **sem origem**.

---

## 1. Quem já construiu (referências)

| Referência | O que mostra |
|---|---|
| [SEOJuice — "I Built a GSC Dashboard for $0" (Vadim Kravcenko, mai/2026)](https://seojuice.com/blog/gsc-search-console-api-for-founders-diy-dashboard/) | Conta de serviço em vez de OAuth (sem refresh token nem tela de consentimento), cron diário, janela terminando em hoje − 2 dias, alertas no Slack, aviso sobre o balde `(anonymized)` e a dica de cruzar página × consulta para achar "vazamento de CTR" |
| [CrawlSEO (github.com/crawlseo/crawlseo, MIT)](https://www.framer.com/community/posts/6j6jR87q2XBdZ27LnpqUUR/) · [guia de SEO self-hosted](https://glukhov.org/web-infrastructure/seo/self-hosted-seo-tools-and-platforms/) | Painel open source: Next.js + Postgres + Prisma, sincroniza GSC (OAuth), Core Web Vitals via PSI, oportunidades de CTR baixo, alertas. É o mais próximo do que queremos. Não verifiquei o repositório diretamente |
| [Nannuka/Google-Search-Console-Archive](https://github.com/Nannuka/Google-Search-Console-Archive) | Arquivo diário do GSC com conta de serviço como usuário "Restrito" da propriedade |
| [joshcarty/google-searchconsole](https://github.com/joshcarty/google-searchconsole) · [gsc_wrapper](https://github.com/antoineeripret/gsc_wrapper) · [JC Chouinard](https://www.jcchouinard.com/google-search-console-api-with-python/) | Bibliotecas e tutoriais Python que fazem a paginação com `startRow` |
| [Coupler — GSC → PostgreSQL "antes que o Google apague"](https://blog.coupler.io/how-to-connect-search-console-to-postgresql/) · [Airbyte](https://airbyte.com/how-to-sync/google-search-console-to-postgresql-destination) · [CloudQuery](https://www.cloudquery.io/hub/export-data/google-search-console/postgresql) | Conectores prontos GSC → Postgres. Confirmam o motivo principal: guardar além dos 16 meses |
| [Exportação em massa para BigQuery (Google, 2023)](https://developers.google.com/search/blog/2023/02/bulk-data-export) · [guia Trevor Fox](https://trevorfox.com/2023/03/google-search-console-bulk-export-for-bigquery/) | Exportação diária oficial, sem limite de linhas. Exagero para um site pequeno |
| [Supabase Cron (pg_cron + pg_net)](https://supabase.com/docs/guides/cron/quickstart) · [crontap: armadilhas](https://crontap.com/guides/supabase-cron-jobs) | Agendamento da edge function. O `pg_net` dispara e não verifica o resultado: não faz retry e não alerta, então a função precisa registrar o próprio status |

**X/Twitter:** a busca não achou threads indexadas de devs indie com GSC + Supabase. Os relatos públicos encontrados são posts de blog (acima). Não inventei referência.

**Arquitetura comum (consenso das fontes):**
1. Autenticação: **conta de serviço**, com o e-mail dela adicionado como usuário (Restrito basta) na propriedade. O OAuth do usuário só aparece em produtos multi-cliente.
2. Agendamento: **cron diário** que puxa os últimos ~3–5 dias e regrava por upsert, porque os dados recentes ainda mudam.
3. Armazenamento: uma linha por **data × página × consulta** (às vezes também × dispositivo e × país), mais uma tabela de totais por data × página.
4. Cuidados: cotas de carga, atraso de ~2 dias, consultas anonimizadas e histórico de só 16 meses.

## 2. Search Console API — detalhes práticos

- **Autenticação:** crie um projeto no Google Cloud, ative a "Google Search Console API", crie a conta de serviço e baixe a chave JSON. Depois, no Search Console, em Configurações → Usuários e permissões, adicione o e-mail `…@….iam.gserviceaccount.com` com permissão **Restrito**. Sem isso a API devolve 403 ([SEOJuice](https://seojuice.com/blog/gsc-search-console-api-for-founders-diy-dashboard/)). Escopo: `https://www.googleapis.com/auth/webmasters.readonly` ([referência do query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)). No Deno, o JWT da conta de serviço é assinado com `jose` e trocado por um token em `oauth2.googleapis.com/token`.
- **Propriedade:** prefira a de domínio, `sc-domain:contemmagia.com.br`, e filtre as páginas de venda com `dimensionFilterGroups` (`page` + `includingRegex`).
- **`searchanalytics.query`** ([doc](https://developers.google.com/webmaster-tools/v1/searchanalytics/query)):
  - dimensões: `date`, `hour`, `page`, `query`, `country`, `device`, `searchAppearance`;
  - `type`: `web` | `image` | `video` | `news` | `discover` | `googleNews`;
  - `dataState`: `final` (padrão) | `all` (inclui dados frescos) | `hourly_all`;
  - `rowLimit` até **25.000**, com paginação por `startRow`;
  - as datas seguem o **fuso do Pacífico**. Atenção ao cruzar com pedidos em horário de Brasília;
  - `metadata.first_incomplete_date` diz a partir de que dia o dado ainda vai mudar.
- **Limites:**
  - exportação de no máximo **50.000 linhas por dia, por site e por tipo de busca** ([Google, deep dive 2022](https://developers.google.com/search/blog/2022/10/performance-data-deep-dive?hl=es)). Para um site pequeno, isso nunca vai ser atingido;
  - cota de Search Analytics: **1.200 QPM** por site e por usuário, e 30 milhões de QPD por projeto. Existe também uma "cota de carga" em janelas de 10 minutos e de 1 dia; agrupar por página **e** consulta é o mais caro ([Usage limits](https://developers.google.com/webmaster-tools/limits)).
- **Atraso:** o dado final fica pronto em ~2–3 dias. O dado fresco (`dataState=all`) chega em poucas horas, mas muda depois ([Google, dez/2024](https://developers.google.com/search/blog/2024/12/recent-data-search-console)). Já houve incidente com mais de 84 h de atraso ([SEL](https://searchengineland.com/google-working-on-fixing-latency-issues-with-the-search-performance-reports-443857)).
- **Anonimização:** consultas raras são omitidas para proteger a privacidade. Por isso a soma de página × consulta **fica menor** que o total da página. Guarde os dois níveis. Na exportação para BigQuery, essas consultas viram linhas agregadas e marcadas ([Google](https://developers.google.com/search/blog/2023/02/bulk-data-export), [SEL](https://searchengineland.com/google-search-console-adds-daily-bulk-data-exports-to-bigquery-393380)).
- **Retenção:** 16 meses. No primeiro dia, faça o backfill dos 16 meses e depois acumule.
- **URL Inspection API** (`urlInspection.index.inspect`): devolve se a página está indexada, a canônica escolhida pelo Google, a última rastreada, a cobertura e a usabilidade. Cota de **2.000/dia e 600/min por propriedade** ([Google](https://developers.google.com/search/blog/2022/01/url-inspection-api), [limits](https://developers.google.com/webmaster-tools/limits)). Rodar uma vez por semana em todas as rotas cabe com folga.
- **Sitemaps API** (`sitemaps.list`): mostra o status do sitemap e a contagem de URLs enviadas.

## 3. Complementos no mesmo painel

- **CrUX API** (dados reais de Core Web Vitals do Chrome) ([doc](https://developer.chrome.com/docs/crux/api)):
  - consulta por `url` ou `origin` e por `formFactor` (PHONE, TABLET, DESKTOP), com p75 de LCP, INP, CLS, FCP e TTFB;
  - média móvel de 28 dias, atualizada diariamente por volta das 04:00 UTC;
  - **150 consultas/min por projeto, grátis**, sem opção de pagar por mais cota;
  - página com pouco tráfego devolve 404 (sem dado). Nesse caso, use a origem;
  - a **CrUX History API** dá a série semanal.
- **PageSpeed Insights API** ([doc](https://developers.google.com/speed/docs/insights/v5/get-started)): dado de laboratório (Lighthouse). Funciona sem chave, mas com chave é melhor para rodar automático. O próprio Google avisa que vai retirar o dado de campo (`loadingExperience`) da PSI e recomenda a CrUX. O cm-pages já tem o `medir.py` para a PSI. No painel, a CrUX basta.
- **Bing Webmaster API** ([acesso, Microsoft](https://learn.microsoft.com/en-ca/bingwebmaster/getting-access)):
  - acesso por chave de API ou OAuth, com uma chave por usuário valendo para todos os sites;
  - `GetQueryStats`, `GetPageStats` e `GetPageQueryStats` recebem só o `siteUrl`, sem intervalo de datas, e devolvem o histórico em **baldes semanais** ([Analytics Edge](https://bing-webmaster-api.analyticsedge.com/getquerystats/));
  - no Brasil o Bing é pequeno: vale como item 2, opcional.

## 4. Atribuir a venda à busca orgânica (página estática, sem UTM)

### Como o GA4 define (referência para ficarmos consistentes)
- **Organic Search:** a origem está na lista de buscadores do Google **ou** o meio é exatamente `organic`. Visitas vindas do **AI Overviews e do AI Mode do Google contam como Organic Search** ([GA4, canais padrão](https://support.google.com/analytics/answer/9756891)).
- **AI Assistant:** canal novo, com meio `ai-assistant` ou referrer de uma lista de assistentes (ChatGPT, Gemini, Copilot, DeepSeek, Grok…) (mesma fonte).
- Sem origem nem meio, a visita cai em **Direct**.

### Método validado
1. **Na chegada** (script leve na página de venda), na ordem:
   - a URL tem `utm_*`, `gclid`, `gbraid`, `wbraid` ou `fbclid`? Use isso (pago ou campanha);
   - senão, olhe o host do `document.referrer`:
     - `google.*`, `bing.com`, `duckduckgo.com`, `search.yahoo.com`, `yandex.*`, `ecosia.org`, `search.brave.com` → `source=<buscador>`, `medium=organic`;
     - `android-app://com.google.android.googlequicksearchbox` → Google (app ou Discover);
     - `chatgpt.com`, `perplexity.ai`, `gemini.google.com`, `copilot.microsoft.com`, `claude.ai` → `medium=ai-assistant`;
     - outro host externo → `referral`;
     - vazio → `direct`;
   - referrer do próprio domínio (`contemmagia.com.br`) **não sobrescreve** a origem já gravada.
2. **Guardar a origem** em `localStorage` e em um cookie first-party `Domain=.contemmagia.com.br` de ~90 dias. O `pay.` é o mesmo site, então o checkout também consegue ler o cookie:
   - **primeiro toque**: gravado uma vez, nunca sobrescrito;
   - **último toque não-direto**: regravado a cada chegada com origem conhecida. É a mesma lógica do GA4 de "último clique não-direto".
3. **Levar ao checkout:** o script que já existe acrescenta os parâmetros ao link só quando faltarem:
   - `utm_source` e `utm_medium` com o último toque não-direto;
   - parâmetros próprios: `lp` (página de entrada), `ref` (host do referrer), `ft` (primeiro toque compacto, ex.: `google|organic|/eba|2026-10-12`).
   - Injetar `utm_source=google&utm_medium=organic` é coerente com a classificação do GA4. **Nunca sobrescreva UTM existente.**
   - Efeito colateral: se o `pay.` tiver GTM, GA4 ou pixel, eles leem esse `utm_*` como campanha manual. Isso substitui a atribuição da sessão lá e transforma um salto interno em "nova campanha".
   - Alternativa mais limpa (recomendada): reservar `utm_*` para campanhas reais e levar a origem detectada em parâmetros próprios (`canal`, `lp`, `ref`, `ft`). O dono escolhe.
4. **No checkout:** gravar no pedido os campos `utm_*`, `canal` (organico, pago, ia, social, email, referral, direto), `ref_host`, `landing_page`, `first_touch` (jsonb) e `gclid`/`fbclid`. Ler da URL e, se faltar, do cookie.

### Limitações (conhecidas e documentadas)
- **O Google não passa a palavra buscada** (o referrer vem só como `https://www.google.com/`). A ligação com a palavra é estatística: página × dia no Search Console.
- **Safari/ITP, referrer:** o Safari reduz o referrer entre sites à origem, mas a origem é o que basta ([WebKit](https://webkit.org/blog/9661/preventing-tracking-prevention-tracking/), [bug 215163](https://bugs.webkit.org/show_bug.cgi?id=215163)).
- **Safari/ITP, armazenamento:** o Safari apaga cookie criado por JS (`document.cookie`) **e também `localStorage`** depois de 7 dias sem interação com o site ([WebKit, mar/2020](https://webkit.org/blog/10218/full-third-party-cookie-blocking-and-more/), [resumo](https://mjtsai.com/blog/2020/03/26/safari-13-1-third-party-cookie-blocking-and-7-day-script-writeable-storage/)).
  - Ter "localStorage + cookie JS" como redundância não adianta no iPhone: os dois expiram juntos.
  - Para guardar o primeiro toque por mais tempo, o cookie precisa ser **gravado pelo servidor** (cabeçalho `Set-Cookie`). Como o site passa pelo Cloudflare, um Worker ou uma regra de resposta pode regravar o cookie (ver build 3).
- **Apps** (Instagram, WhatsApp, app do Google, Discover): às vezes não mandam referrer, e a visita vira "direto". O Discover aparece como `android-app://…googlequicksearchbox` ou sem referrer ([Netpeak](https://netpeak.us/blog/how-to-track-traffic-from-google-discover-in-ga4-and-google-search-console/), [Plausible #1337](https://github.com/plausible/analytics/discussions/1337)). No Search Console, o Discover é um `type` separado.
- **AI Overviews e AI Mode** chegam como Google orgânico, sem como separar.
- **ChatGPT** adicionava `utm_source=chatgpt.com`. Há relatos (out/2026, não confirmados pela OpenAI) de que parou de mandar UTM e referrer, o que joga essas visitas em "direto" ([Relevant Audience](https://www.relevantaudience.com/analytics/chatgpt-gpt-6-utm-referrer-dropped-direct-traffic/), [Profound](https://www.tryprofound.com/blog/chatgpt-missing-utm-tags)).
- Bloqueadores de anúncio não afetam isto: o script é próprio, não é GA. Página aberta direto no checkout (link salvo) fica sem origem, a não ser pelo cookie.
- A compra costuma acontecer dias depois da primeira visita: daí guardar os dois toques e comparar.

### Cruzar com o Search Console
- **Vendas orgânicas por página de entrada e dia** junto com **cliques do Search Console da mesma página e dia** dão a conversão orgânica da página (vendas ÷ cliques) e a receita por clique.
- **Receita estimada por consulta** = cliques da consulta na página × conversão orgânica da página. Isso é estimativa: o rótulo no painel tem que dizer "estimado".
- Ajuste o fuso: o Search Console usa o horário do Pacífico, e os pedidos usam o de Brasília. Agregue por semana para o efeito sumir.

## 5. Desenho recomendado para nós

**Como é hoje:** o dono não vê no sistema quanto a busca orgânica traz nem vende por página. A venda orgânica chega ao checkout sem origem.
**Como fica:** uma tela com cliques, impressões, CTR e posição por página e por palavra, histórico além de 16 meses, oportunidades de melhoria, Core Web Vitals reais, status de indexação e vendas orgânicas por página.
**O que muda na tela:**
- uma aba "SEO" nova no sistema interno;
- nas páginas de venda, nada visível.

**Efeitos colaterais:**
- o link do checkout ganha os parâmetros `utm_source`/`utm_medium` (quando faltam), `lp`, `ref` e `ft`;
- o checkout precisa aceitar e gravar esses campos. Isso é mexer em checkout: passa por validação do dono;
- o cookie novo é first-party, sem dado pessoal.

**Custo:**
- APIs: R$ 0 (GSC, CrUX, URL Inspection e Bing são gratuitas; PSI tem cota diária gratuita);
- armazenamento: dezenas de milhares de linhas por mês, desprezível no Supabase;
- construção: média, 5 builds e 1 opcional.

### Builds (ordem)
0. **Configuração (manual, ~20 min do dono):**
   - criar o projeto no Google Cloud e ativar as APIs Search Console e Chrome UX Report;
   - criar a conta de serviço e a chave JSON e guardar no secret do Supabase;
   - adicionar o e-mail da conta como **Restrito** na propriedade `sc-domain:contemmagia.com.br`. Se a propriedade de domínio não existir, verificar por DNS no Cloudflare;
   - criar uma chave de API para a CrUX.
1. **Coleta GSC (edge function + cron):**
   - tabelas `seo_gsc_pagina_dia` (data, página, cliques, impressões, ctr, posição) e `seo_gsc_consulta_dia` (data, página, consulta, dispositivo, …), com chave única e upsert;
   - função `seo-gsc-sync`: no primeiro uso faz o backfill de 16 meses (mês a mês); depois, todo dia, regrava os últimos 5 dias;
   - log de execução em `seo_sync_execucao`, porque o `pg_net` não avisa falha;
   - pg_cron diário (~10:00 BRT).
   - Aceite: a soma de cliques de um dia bate com a tela do Search Console.
2. **CrUX + indexação (mesma função ou irmã, semanal):**
   - CrUX por URL das rotas ativas (com fallback para a origem);
   - URL Inspection de cada rota (bem abaixo dos 2.000/dia);
   - tabelas `seo_cwv_semana` e `seo_indexacao`.
3. **Origem na página (cm-pages):**
   - estender o `CHECKOUT_JS` do `estatico.py` com a classificação do referrer, o primeiro e o último toque (cookie `.contemmagia.com.br`) e os parâmetros extras no link;
   - para o primeiro toque sobreviver aos 7 dias do Safari, regravar o cookie pelo servidor (Cloudflare Worker ou regra de resposta);
   - republicar as páginas, com pedido de publicação.
   - Aceite: abrir com referrer simulado do Google e conferir o link do checkout.
4. **Origem no pedido (checkout, fluxo financeiro com validação):**
   - o checkout lê os parâmetros e o cookie e grava as colunas de origem no pedido;
   - não altera valor nem fluxo de pagamento.
5. **Tela "SEO" no sistema:**
   - resumo de 28 dias contra os 28 anteriores;
   - tabela de páginas, com as consultas de cada página;
   - "oportunidades" (posição 4–15, impressões altas e CTR abaixo do esperado);
   - Core Web Vitals por página e status de indexação;
   - vendas orgânicas, conversão por clique e receita estimada por palavra (marcada como estimativa).
6. *(Opcional)* **Bing:** sincronização semanal de `GetPageQueryStats`. Alertas (queda de cliques acima de X%, página desindexada) por WhatsApp ou e-mail.

**Alternativa descartada:** exportação em massa para BigQuery. Não tem limite de linhas, mas exige um projeto BigQuery com cobrança e um segundo banco, e o site é pequeno demais para precisar disso.
