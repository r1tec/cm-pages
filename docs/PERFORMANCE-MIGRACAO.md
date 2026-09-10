# Recuperação de desempenho após migração — 10/09/2026

## Pedido e decisão atual

O dono estabeleceu nota mínima 90 para as páginas de contemmagia.com.br e pediu
investigação da regressão após a migração para eduparmeggiani.com. O pedido
atual prioriza recuperar o desempenho anterior. Restaurar o carregamento GTM
por interação, com espera passiva de até cinco segundos explicitamente autorizada,
sem retirar tags nem mudar seus IDs.
Consequência informada no chat: uma visita que sai antes desse prazo e sem
interagir pode não ser registrada, como no comportamento anterior à migração.

## Causa encontrada

- DRB e MPG: HTTP 200 direto nos dois domínios, sem redirecionamento entre eles.
  Cloudflare em contemmagia.com.br entrega HTML comprimido, cache HIT/MISS,
  respostas rápidas na amostra. Não há evidência para desligá-lo ou mudar DNS.
- Commit `0c51ac5` de 10/09 11:24 BRT trocou a espera do GTM pelo carregamento
  imediato, junto da migração. Backups antes/depois em
  `.build/gtm-original-backup/20260910T141858519923Z/` comprovam a troca.
- Teste controlado local Lighthouse 12.8.2 no MPG, mesma URL/HTML e apenas a
  estratégia GTM diferente: imediato 83, LCP 3,1s, TBT 410ms; anterior 93,
  LCP 3,1s, TBT 50ms. A auditoria inicial termina antes de carregar as tags na
  versão anterior. Portanto esse teste mede o benefício da separação inicial;
  também testar as tags após o prazo e após interação real.
- A investigação anterior do DRB identificou o peso das tags, mas não localizou
  a mudança simultânea que o colocou na abertura. Ela foi insuficiente para
  explicar a regressão geral. Chat não explica a queda no MPG.

## Execução e aceite

1. Restaurar a estratégia no normalizador compartilhado; manter modo imediato
   explícito para reversão. Inicializar dataLayer cedo para preservar a fila.
2. Pilotar DRB e MPG com `./publicar.sh --gtm-performance --aplicar drb mpg`.
   O modo restrito usa o HTML publicado, salva backup, compara conteúdo antes da
   troca, substitui somente GTM e limpa cache; não publica edições locais alheias.
3. Verificar carregamento por tempo e interação, uma instância, tags/pixels,
   checkout com UTM, chat do DRB e FAQ. Repetir PageSpeed móvel/desktop.
4. Aplicar às demais páginas afetadas e medir o conjunto. Se alguma ficar abaixo
   de 90, investigar seus audits; não escolher somente a melhor rodada.

Tem que fazer: atingir e verificar a meta, preservar IDs e configuração das tags,
mesmo conteúdo e layout, rotas e checkout; estratégia igual para todos os visitantes.
Não pode acontecer: excluir tags, duplicar eventos, mudar campanhas/DNS, perder
alterações locais alheias, atrasar o chat além do combinado ou esconder conteúdo
para manipular a auditoria. Não afirmar garantia absoluta sobre uma nota variável.

## Continuidade

Normalizador: `rastreamento.py`. Publicação integral usa a estratégia de desempenho.
`--gtm-original` continua significando GTM imediato da referência WordPress;
`--gtm-performance` restaura o comportamento que existia nas páginas estáticas.
O histórico de Core Web Vitals de 28 dias é independente da nota Lighthouse atual.
Resultados e limites da validação estão registrados abaixo.

### Ajuste explicitamente autorizado após o piloto

Resposta do dono: **"Aceito até 5 segundos para priorizar desempenho"**, mantendo
início imediato na primeira interação e aceitando a possível perda de registro
de visitas que saem antes disso sem interagir. Esse limite substitui os três
segundos do primeiro piloto. O normalizador agora aplica cinco segundos.
MPG também teve troca de fonte observada causando deslocamento de texto: antecipar
Montserrat por preload, sem trocar fonte, conteúdo ou dimensões finais.

## Correções publicadas

- Todas as oito páginas: GTM uma única vez, na primeira interação ou após 5s.
  A fila `dataLayer` existe desde o início. O container e os dois pixels foram
  preservados. O chat do DRB permanece após 12s.
- Cache: URLs limpas já tinham o GTM novo, mas URLs previamente visitadas com
  `utm_source=gtm-verification` e `utm_source=chat-check` ainda entregavam 3s ou
  carregamento imediato. `limpar_cache.py` passou a invalidar por prefixo,
  incluindo assets e qualquer query string. Confirmado MISS e versão nova nas
  duas URLs antes obsoletas. Sem alteração de DNS ou regras de roteamento.
  Referência: [Cloudflare — purge by prefix](https://developers.cloudflare.com/cache/how-to/purge-cache/purge_by_prefix/).
- MPG: preload da Montserrat para reduzir o deslocamento na troca de fonte.
- BCE: Montserrat WOFF2 com conjunto latino e caracteres usados pela página,
  embutida como fonte crítica; CLS passou de aproximadamente 0,236 para zero.
- ECM-26-v1: quatro pesos da Cera Pro convertidos/subconjuntados em WOFF2,
  preservando caracteres da página, Latin-1, pontuação e recursos OpenType.
  HTML caiu de aproximadamente 405KB para 138KB. Fontes originais preservadas
  na fonte HTML; `desempenho.json` aplica as variantes no build. Preload do fundo
  principal e fundos secundários por IntersectionObserver, 600px antes da tela,
  com fallback completo sem JavaScript. Removido `/~flock.js`, resíduo do editor
  que retornava 404. Reservada a proporção 453/201 do logo para não empurrar a
  seção seguinte no celular. Texto, ofertas e dimensões finais preservados.

## PageSpeed público após as correções

API oficial, URLs `https://contemmagia.com.br/<slug>/`, mobile e desktop.
Últimas medições bem-sucedidas da versão final de cada página em 10/09/2026:

| Página | Celular | Desktop |
|---|---:|---:|
| DRB | 96 | 100 |
| MPG | 92 | 99 |
| BCE | 96 | 99 |
| COE | 95 | 99 |
| MCE | 98 | 100 |
| GDP | 99 | 99 |
| ECM-26 | 97 | 99 |
| ECM-26-v1 | 93 | 97 |

BCE final: 20:57 UTC, LCP 2,7s/0,6s, TBT zero, CLS zero.
ECM-26-v1 final: 20:59 UTC, LCP 3,0s/1,0s, TBT zero, CLS 0,020/0,014.
Não são promessas de nota constante: API teve respostas 500 e variação entre
rodadas. Não selecionar uma rodada alta para encobrir uma regressão pendente.
Nas etapas intermediárias, ECM chegou a 69–79 mobile e 68 desktop; a comparação
acima é após fontes, carregamento de fundos e reserva de espaço do logo.
BCE mostrou 83 numa consulta logo após publicar, mas 92 com nova URL e 96 na
URL limpa final, ambas sem CLS. Sempre conferir horário e HTML da medição.

## Provas de funcionamento e limites

- Oito páginas testadas por tempo e por interação: uma instância GTM, um evento
  `gtm.js`, dois pixels inicializados, checkout propagando UTM, sem erros JS.
  BCE e ECM-26-v1 novamente testados após as otimizações.
- DRB publicado: chat solicitado em 12,0s, pronto em 12,8–13,3s; abrir/fechar
  confirmado em 390px e 1440px. Checkout com UTM e FAQ funcionaram inclusive
  bloqueando o serviço do chat; nenhum erro JavaScript.
- Normalizador idempotente e reversível nos oito HTMLs; rejeita carregador
  duplicado. Limpeza de cache testada para payload, slug inválida e falha da API.
- Testes locais de fontes preservaram textos e dimensões dos títulos. Fundos do
  ECM comparados em 390px/1440px com/sem JavaScript e após rolagem: imagens e
  dimensões iguais. No-JS não depende do observador para mostrar os fundos.
- O navegador de teste carregou as configurações dos dois pixels sem falha, mas
  não observou requisições `facebook.com/tr/`, tanto com 5s quanto no controle
  imediato. Isso não comprova entrega de PageView ao painel Meta. A configuração
  das tags não foi alterada; eventual validação de eventos no painel é separada.
- Os avisos preexistentes de contraste do MPG/ECM antigo foram preservados, pois
  esta correção não muda cores nem conteúdo. Não confundir nota de desempenho
  com acessibilidade nem com aprovação dos Core Web Vitals dos últimos 28 dias.

Para futuras publicações, usar sempre `./publicar.sh`, verificar a URL limpa e
uma campanha previamente cacheada e medir após o deploy. Para reverter o GTM,
`./publicar.sh --gtm-original --aplicar <slugs>` é explícito e perderá a espera
autorizada; não executá-lo como normalização automática. As otimizações por
página ficam em `desempenho.json`, sem alterar as demais páginas.
