# Revisão de rastreamento e desempenho — 17/09/2026

Escopo: DRB, BCE, BPV, MPG, MCE, COE, GDP, ECM-26 (`contemmagia.com.br/<slug>/`).
Somente diagnóstico; nada foi alterado ou publicado nesta revisão. Testes de navegador com
envios à Meta/Google abortados (sem visitas ou eventos falsos).

## Estado atual

Rastreamento:
- PageView Meta cedo nas 8 páginas, 1 por pixel, sem duplicidade; entrega com link de
  campanha liberada pela correção do CSP (ver `AUDITORIA-META-ANTECIPADA-2026-09-17.md`).
- Cookies `_fbp` e `_fbc` criados em `.contemmagia.com.br` (compartilhados com o checkout).
- Links de compra repassam UTMs e `fbclid` para `pay.contemmagia.com.br/c/<slug>`.
- Checkout dispara InitiateCheckout nos 2 pixels com fbp/fbc (~3,3s após abrir, sem `eid`).
- GTM v28 (5s ou 1ª interação): GA4, Google Ads (remarketing + conversão), Clarity,
  PageView Meta (suprimido pelo carregador), Lead só em URLs `obrigado`. A tag Meta de
  clique nos botões (id 23) está **pausada**. Nenhum evento de engajamento vai à Meta:
  quem lê a oferta e sai é igual a quem sai em 1 segundo.

Desempenho (PageSpeed celular, 1 amostra cada, 17/09):

| Página | Nota | LCP | TBT |
| --- | --- | --- | --- |
| DRB | 70 | 4,2s | 550ms |
| BCE | 81 | 4,8s | 40ms |
| BPV | 90 | 3,1s | 160ms |
| MPG | 84 | 4,3s | 50ms |
| MCE | 75 | 4,9s | 240ms |
| COE | 85 | 3,8s | 200ms |
| GDP | 78 | 4,9s | 200ms |
| ECM-26 | 80 | 4,4s | 160ms |

Antes da antecipação Meta (12/09) as mesmas páginas mediam 96–100 no celular, LCP ~2s.

## Achados

1. **SDK Meta no momento crítico.** `fbevents.js` + 2 configurações = ~215 KB transferidos,
   ~900 KB de JavaScript, pedidos junto da imagem principal em todas as páginas.
   Laboratório (CPU 4×, 4G, mediana de 5): ~150ms de tarefas longas nos primeiros 6s com
   o SDK, 0ms sem ele. Coincide com a queda 96–100 → 70–90 medida após a antecipação.
2. **Imagens fora da primeira tela baixando no início (celular).**
   MCE 10 imagens/~640 KB e MPG 10/~700 KB (fundos `::before` de 5 seções + fotos);
   BCE 10/~360 KB; GDP 9/~400 KB; DRB 5/~165 KB. DRB/BCE/GDP: posters dos 4 vídeos de
   depoimento (vídeos já com `preload="none"`). BPV, COE e ECM-26 já estão enxutas.
   A DRB tem `cm-background-loader` para fundos; as demais não.
3. **Sem sinal de engajamento para remarketing** (ver estado atual).

## Recomendações (ordem sugerida)

1. **Visita registrada na hora, SDK depois.** No início do HTML, script mínimo (~1 KB):
   cria/reaproveita `_fbp`/`_fbc` no formato da Meta e envia PageView aos 2 pixels por
   requisição leve a `facebook.com/tr` (mesmos dados principais: URL, referrer, fbp, fbc).
   O SDK completo passa a carregar junto do GTM (5s/interação), com o PageView inicial
   suprimido como hoje. Esperado: registro antes do atual (0,4–1,5s → primeiros ms) e
   retorno da nota perto do patamar anterior. Risco: o envio leve não leva metadados
   automáticos do SDK; validar no Gerenciador de Eventos (Testar eventos + qualidade de
   correspondência) em uma página piloto antes de expandir. Reversão por `rastreamento.json`.
2. **Evento de engajamento para remarketing.** Um evento quando a seção de preço/oferta
   aparece na tela e um após ~30s de leitura ativa, enviados aos 2 pixels, uma vez por
   visita. Permite públicos "viu a oferta e não comprou". Custo desprezível (observador
   de visibilidade + temporizador). Nomes personalizados, para não inflar
   InitiateCheckout/ViewContent usados em otimização de campanha sem decisão do dono.
3. **Adiar imagens fora da primeira tela** em MCE, MPG, BCE, GDP e DRB, reaproveitando o
   carregador de fundos da DRB (antecedência de 800px) e aplicando o mesmo aos posters.
   Sem mudança visual; conferir capturas em 390/1440px.

Fora por ora (não megalomaníaco): API de Conversões no servidor para PageView, mudança de
eventos no checkout, novas tags GTM. Reavaliar depois de medir o item 1 no painel Meta.

## Provas locais

Scratchpad da sessão: `psi/*.json` (PageSpeed), `pw/perf.cjs` (A/B laboratório),
`pw/img.cjs` (imagens), `pw/k.cjs` e `pw/l.cjs` (cookies, links e checkout).
