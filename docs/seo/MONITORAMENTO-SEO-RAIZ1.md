# Monitoramento de SEO no Raiz1 — concepção

Data: 2026-10-19. Base: `PESQUISA-MONITORAMENTO-2026-10-19.md` (método e fontes) +
leitura do repo raiz1-lovable (`origin/main`). Construção acontece no raiz1-lovable,
em branch própria, só depois do "pode construir" do dono.

## O que dá para medir

| Pergunta do dono | Medida | De onde vem |
|---|---|---|
| O Google está mostrando minhas páginas? | impressões (vezes que apareceu na busca) | Search Console |
| As pessoas clicam? | cliques e CTR (cliques ÷ impressões) | Search Console |
| Em que lugar apareço? | posição média por página e por busca | Search Console |
| O que as pessoas digitaram? | buscas (consultas) por página | Search Console (buscas raras vêm ocultas) |
| O Google guardou a página? | status de indexação por página | Search Console (URL Inspection) |
| A página é rápida para quem visita? | Core Web Vitals reais (LCP, INP, CLS) | Chrome UX Report (só com tráfego suficiente) |
| Quanto vendi pela busca? | vendas e receita com `utm_medium=organic` | pedido no checkout do Raiz1 |
| A página converte? | vendas ÷ cliques do Google, por página | cruzamento das duas fontes |
| E o Bing? | cliques/impressões do Bing | Bing Webmaster (opcional) |

Não dá para medir: a palavra exata que gerou cada venda (o Google não informa);
dados com menos de ~2 dias; histórico além de 16 meses se não for guardado por nós.

## O que o Raiz1 já tem (viabilidade: alta)

- **Origem da venda já é gravada.** O checkout `/c/:slug` lê as UTMs da URL
  (`useCheckoutTracking.ts`) e a edge `create-checkout-order` grava em
  `checkout_orders.url_utm_source/medium/...`. Desde 19/10/2026 as páginas do
  cm-pages mandam `utm_source=google|bing&utm_medium=organic` para visita de
  buscador — a venda orgânica já cai no pedido, sem mexer no checkout.
- **Painel de tráfego existe:** `src/pages/Trafego.tsx` (aba de Análises), com
  componentes em `src/components/dashboard/`, gráficos `recharts`.
- **Padrão de coleta agendada existe:** edge + `pg_cron` + `net.http_post` com
  `x-internal-secret`, log em `traffic_sync_log` (coletor da Meta).
- **Conta de serviço Google já usada** (`GOOGLE_DRIVE_SA_JSON`, Drive): o mesmo
  padrão serve para a API do Search Console.
- **Multi-tenant:** tudo por `app_company_id`; a propriedade do Search Console e a
  credencial são por empresa; o cron itera empresas (MODELO-TENANCY §4).

Lacunas: não há `gclid`, `referrer` nem página de entrada no pedido (o slug do
checkout já identifica a página); não há coletor Google.

## Tela proposta — aba "SEO" em Análises

1. Cartões (28 dias × 28 anteriores): cliques, impressões, posição média, vendas
   orgânicas, receita orgânica.
2. Gráfico diário: cliques e vendas orgânicas.
3. Tabela por página: cliques, impressões, CTR, posição, vendas, receita,
   conversão; ao abrir, as buscas daquela página.
4. Oportunidades: buscas em posição 4–15 com muitas impressões e CTR baixo.
5. Saúde: indexada sim/não e velocidade real por página.

## Builds (no raiz1-lovable)

0. **Acesso (manual, ~10 min):** ativar a API do Search Console no projeto Google
   da conta de serviço já usada e adicionar o e-mail dela como usuário
   "Restrito" na propriedade `sc-domain:contemmagia.com.br` (conta
   operacoes@raiz1.com.br). Cadastrar a propriedade na configuração da empresa.
1. **Coleta diária do Search Console:** tabelas `seo_gsc_pagina_dia` e
   `seo_gsc_consulta_dia` (com `app_company_id`, chave única, upsert), edge
   `seo-gsc-sync` (primeira vez: 16 meses; depois os últimos 5 dias), log, cron.
   Aceite: soma de cliques de um dia = tela do Search Console.
2. **Saúde semanal:** indexação (URL Inspection) e Core Web Vitals (CrUX) por
   página → `seo_indexacao`, `seo_cwv_semana`.
3. **Aba SEO:** a tela acima, lendo as tabelas novas + `checkout_orders` com
   `url_utm_medium='organic'`, filtrada pela empresa selecionada.
4. *(Opcional)* Bing e alertas (queda de cliques, página fora do índice).

Custo: APIs gratuitas; complexidade média; 3 builds + 1 opcional.
