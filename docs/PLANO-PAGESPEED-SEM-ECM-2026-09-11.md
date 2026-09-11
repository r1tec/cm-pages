# Otimização completa das páginas, exceto ECM

Pedido atual do dono: finalizar BCE (publicação já concluída, faltam medição
final e GitHub) e em seguida aplicar a mesma revisão completa às demais páginas,
excluindo todas as versões do ECM. Autorização inclui ajustes técnicos, validação,
publicação pelo pipeline, limpeza de cache, medição pública e commit/push.
Preservar GTM, conteúdo, compras, vídeos, FAQ e chat onde já autorizado.
Decisão mais recente substitui a parada: em 500/timeout, avisar, registrar
pendência e seguir à próxima tarefa. Retomar após 5/15/30 minutos (até três
retornos no lote), sem tratar erro como nota. PSI pendente não impede GitHub.

## Aceite de cada página

Tem que fazer: obter diagnóstico completo mobile/desktop; avaliar todos os audits,
inclusive ganhos pequenos; implementar o que for viável; comparar fonte/build
com o conteúdo público; validar visual, métricas e funções; publicar apenas a slug
em andamento; conferir versão/cache e PageSpeed; informar resultado antes da próxima.

Não pode acontecer: editar/publicar qualquer ECM; remover GTM ou função importante
para nota; incluir trabalho local alheio no commit; encerrar no teste inicial;
atribuir toda diferença à Cloudflare sem prova; afirmar velocidade constante.

## Ordem e andamento

| Página | Estado |
| --- | --- |
| BCE | Concluída, publicada, 95/99, FCP 1,9s/0,5s; GitHub 6dd1481 |
| COE | Revisada, 99/100, FCP 1,7s/0,3s; sem melhoria adicional indicada, nenhuma nova publicação necessária |
| DRB | Publicada e validada, 94/99, FCP 1,9s/0,4s; retomada resolveu PSI |
| GDP | Versão definitiva publicada e conferida; 98/99 na última medição, oscilação anterior desktop83 registrada |
| MCE | Publicada com FAQ legível; última coleta85/100, mobile TBT420ms em tags; meta mobile pendente |
| MPG | Publicada com FAQ legível; última coleta97/69, desktop TBT1150ms em tags; meta desktop pendente |
| FSA | Publicada e funcional, mobile 97; desktop pendente 500 após primeira retomada |

Hashes iniciais das exclusões (SHA-256 de caminhos e bytes em ordem):
- ecm-26, 6 arquivos: `53fe8bfe96a2c5b0421db5436232369c55f9ce9318ec3669d20f23f2e299f6da`
- ecm-26-v1, 18 arquivos: `3ed2bb78f30fb3dfe44ec410097c8e378b9393a6636efa1565141ed422b99cfb`

Não usar `./publicar.sh` sem slug. Pastas ECM são somente inventariadas por hash
para provar preservação, sem build, medição ou publicação. Consumo real de tokens
por tarefa não exposto pelo ambiente. Guardar diagnósticos integrais e verificações
em `/tmp`, com resumo e referências persistentes neste relatório.

## COE

47 audits por dispositivo examinados em `/tmp/psi-lote/coe-antes.json`.
14:50:36 UTC mobile 99, FCP/LCP 1,7s, TBT/CLS zero; desktop 14:51:14 UTC
100, FCP 0,3s, LCP 0,4s, TBT/CLS zero. Sem savings de CSS/JS/imagens/documento.
Fontes externas remanescentes já são subconjuntos (3,9–5,3KB transferidos), abaixo
da primeira tela. Não embutir fontes indiscriminadamente nem aumentar o HTML.
Árvore sem candidatos de preconnect. Beacon Cloudflare 4/11KiB (cache/legado)
mantido. Reflow de 44–45ms sem atribuição; sem causa segura para alteração.
Fonte bundler construída para inspeção, sem publicar: pipeline já reduz capa,
imagens e cores. Aviso de script removido não autoriza nova publicação sem prova
de funções; como não houve ajuste aplicável, preservada a versão pública existente.

## DRB

Diagnóstico inicial em `/tmp/psi-lote/drb-antes.json`: mobile 97, FCP 1,4s,
LCP 2,6s, TBT/CLS zero (14:53:39 UTC); desktop 100, FCP 0,5s, LCP 0,6s,
TBT/CLS zero (14:54:15 UTC). 47 audits por dispositivo examinados.
Sem economia de imagens/CSS/JS. Roboto ainda inteira na árvore de rede (~44KB
transferidos); reduzida da original de 43.136 para 23.876 bytes, com cobertura
de todo o texto e métricas iguais. Fonte abaixo da dobra sem preload antecipado.
GTM e carregador de chat preservados. Reflow sem atribuição, sem leituras
geométricas no JS próprio; cache/legado do beacon mantidos para preservar medição.

Publicada com purge de assets e campanhas. 288 nós de texto e caixas preservados
em oito larguras; sete CTAs/UTM, cinco FAQs, imagens e contraste aprovados. Chat
público: loader aos 12.000/12.004ms, uma instância, abre/fecha em 390/1440;
compras/FAQ também funcionam com fornecedor bloqueado. Nenhum erro JS.
Desktop final 99, FCP 0,4s, LCP 0,5s, TBT/CLS zero (14:57:55 UTC).
Mobile retornou 500 às 14:57:50 UTC: pendente, primeira retomada a partir de
**15:02:50 UTC**, sem bloquear GDP. Evidências `/tmp/psi-lote/drb-depois.json`,
`/tmp/drb-lote-post-validacao.json` e screenshots `/tmp/drb-lote-post-*.png`.

Primeiro retorno mobile expirou às 15:06:49 UTC; segundo retorno elegível
às 15:21:49 UTC, iniciado durante a conclusão de MCE/FSA.

## GDP

Inicial: mobile timeout 15:00:46 UTC; desktop 98, FCP 0,5s/LCP 0,6s.
Diagnósticos completos em `/tmp/psi-lote/gdp-antes.json`: Roboto integral e
image-delivery com 19KiB em logo/mockup. Fonte 43.136 → 23.112 bytes;
imagens responsivas 295/522 e 460/632, mantendo originais para telas densas.
Publicada e cache de assets/campanhas limpo. 221 nós, sete CTAs/UTM, quatro
FAQs e geometria preservados em oito larguras. Evidências em
`/tmp/gdp-lote-post-validacao.json` e `/tmp/gdp-lote-post-*.png`.
Final desktop 99, FCP/LCP 0,5s; mobile inicialmente 500, retomada após cinco
minutos aprovada: 95, FCP 1,8s/LCP 2,6s, TBT/CLS zero.
Restantes: mockup em tela densa mantém maior variante para nitidez; logo aponta
4,5KB de compressão, mas experimentos q80/70/60/50 deram 10.154/10.154/10.150/
10.156 bytes: sem ganho relevante sem degradar transparência. Beacon preservado.
Árvore sem candidato extra de preconnect, demais audits aprovados/não aplicáveis.

## MCE

Inicial mobile timeout; desktop 96, FCP 0,7s/LCP 0,8s. 47 audits recebidos:
Roboto integral; imagem completo e tridente com 35KiB estimados. Fonte reduzida
43.136 → 23.628 bytes e completo com variantes 275/550/860 e preload alinhado.
Tentativa tridente responsivo mudou largura 198 → 130,7px por dimensionamento
intrínseco percentual: revertida, preservando desenho. 218 nós, seis CTAs/UTM,
quatro FAQs e imagens iguais em 390/1440; seis larguras adicionais sem overflow.
Publisher avisou contraste em FAQ com fundo branco; mesmas cores/textos/caixas
da versão anterior, sem alteração de contraste nesta tarefa. Conferir contexto
real do fundo antes de redesenhar. Publicação e purge concluídos.

## MPG

Inicial mobile 98, FCP/LCP 2,0s, TBT/CLS zero; desktop 500. Roboto integral,
imagens rosa/livro/logo com 166KiB estimados. Fonte 43.136 → 23.588 bytes;
variantes da rosa 265/400/598, livro 400/486, logo 400/700/923. Compressão q75
nas fotos; maior resolução preservada. Preload passa a escolher a mesma variante.
219 nós, seis CTAs/UTM, quatro FAQs e dimensões preservados em oito larguras;
conferência pública aprovada. Publisher trouxe aviso de contraste preexistente
em FAQ, sem mudança de cor/desenho nesta entrega. Publicada com purge.
PSI final retornou 500 nos dois dispositivos; retomar após cinco minutos,
mantendo pendência explícita em `/tmp/psi-lote/mpg-depois.json`.

## FSA

Inicial 97/99, FCP 1,8s/0,3s e LCP 2,0s/0,4s, TBT/CLS zero. 47 audits por
dispositivo. unused-javascript é GTM, preservado; unused-css identifica bloco
de fontes críticas realmente usadas, mantido para evitar CLS e troca de fonte.
Image-delivery cita capa já responsiva e fundo de virada. Capa preservada para
recorte/DPR. Fundo agora gerado da exportação original em 640/960/1195, com
12.854/23.110/33.900 bytes (anterior maior 45.572), lazy e sizes considerando
altura do recorte. 370 nós, sete CTAs incluindo offer=alt, nove FAQs e caixas
preservados em oito larguras. Publicação em andamento.

## Conferência final e rodadas adicionais

- Retomada DRB mobile aprovada: 94, FCP 1,9s/LCP 2,8s, TBT/CLS zero.
- Descoberto aumento de bytes em variantes transparentes: GDP logo295 tinha
  10.154B contra original522 8.322B; MCE completo550 45.572B contra860 31.196B;
  MPG logo700 42.254B contra923 24.002B. Gerador agora descarta candidatos
  menores e mais pesados. Configurações mantêm larguras para avaliação, mas o
  srcset só recebe candidatos vantajosos. Teste automatizado cobre essa regressão.
  As três páginas foram novamente validadas e publicadas com purge.
- GDP final 98/83, FCP 1,2s/0,6s e LCP 1,9s/0,6s. Desktop TBT380ms com
  Analytics/Ads/Meta; não atribuir a imagens nem apagar nota menor. Rodada
  anterior 95/99 fica como histórico, não como resultado da versão atual.
- MPG rodada intermediária 96/81, desktop TBT420ms: tarefas maiores atribuídas
  a gtag Analytics178ms, Ads152ms, fbevents148ms, configuração Meta108ms.
  Nova versão de imagens mobile99, FCP1,3s/LCP1,6s e TBT/CLSzero; desktop500.
- MCE versão de imagens96/99, FCP1,5s/0,7s, LCP2,3s/0,7s, TBT/CLSzero.
- FSA publicada97mobile, FCP1,8s/LCP2,0s/TBT0/CLS0; desktop500 às15:25:43UTC.
  Primeira retomada também500; segundo retorno só após15min, sem bloquear lote.
- GTM confirmado uma vez por tempo e interação em GDP/MCE/MPG/FSA:
  5.197/5.040/5.072/5.077ms por tempo e 80/77/76/108ms após interação.
  Sem envio de conversões ou mensagens. Rastreamento preservado.
- Avisos de contraste MCE/MPG investigados em vez de descartados: screenshot
  comprovou FAQ com fundo branco e texto quase invisível. Correção opt-in
  `fundo_acordeao: #1a1919` reproduz fundo da página sem mudar textos/geometria.
  Comparações completas passaram; verificar.py aprovou contraste MCE >=4,5.
  MPG em conferência, ambas serão publicadas e verificadas novamente.
- Hashes ECM conferidos novamente e idênticos aos iniciais.

## Fechamento técnico

Todas as mudanças de página foram publicadas pelo pipeline, com limpeza de cache
de assets/campanhas e comparação pública posterior. COE não precisou de nova
publicação. FAQs MCE/MPG corrigidos e contraste >=4,5 aprovado em ambas; textos,
compras e dimensões preservados. Quatro atalhos FSA testados em390/1440, com
destinos visíveis abaixo do menu (96/60px). Treze testes automatizados passaram,
skill validada e diff da tarefa sem erros de whitespace.

GDP rechecagem desktop99/FCP0,4s/LCP0,5s/TBT0/CLS0 às15:35:53UTC confirma
variação em relação ao83 anterior, sem mudança de código entre as duas.
MCE após correção do FAQ:85/100; mobile FCP2,1s/LCP2,5s/TBT420ms/CLS0,
desktop FCP/LCP0,5s/TBT0/CLS0. As maiores tarefas mobile são Analytics197ms,
Meta180ms, Ads160ms e configuração Meta139ms. Não atribuir a cor do FAQ.
MPG após correção do FAQ:97/69; mobile FCP/LCP2,0s/TBT0/CLS0, desktop
FCP/LCP0,7s/TBT1150ms/CLS0. Tarefas desktop: Analytics325ms, Ads321ms,
Meta263ms, configuração Meta240ms e GTM142ms. Sem cortar rastreamento para nota.
**Meta90 não está validada nessas duas coletas; não declarar lote100% aprovado.**

FSA desktop permanece pendente:500 às15:25:43 e15:31:01UTC; próxima janela
operacional de retorno a partir de15:46:01UTC. Não há tarefa em background
agendada após o encerramento; pendência fica registrada para retomada.

Inventário persistente de todas as coletas, notas e47audits por dispositivo:
`docs/PAGESPEED-AUDITS-SEM-ECM-2026-09-11.json`. Respostas brutas continuam em
`/tmp/psi-lote/`. Achados remanescentes: fontes necessárias da FSA, tamanho
para DPR/recorte, transparência sem economia real ao reduzir, reflow sem causa
própria segura e scripts úteis de medição/anúncios. Recursos de GTM/Ads/Meta
mantidos conforme instrução explícita do dono; ajustes dentro do container
dependem de acesso/configuração não disponíveis neste trabalho.

Commit local da implementação:4874824. Push bloqueado duas vezes pela revisão
automática, inclusive após comprovar origin canônico e pushes anteriores da
mesma tarefa. Motivo: exigência de autorização explícita para enviar esse
payload ao GitHub r1tec/cm-pages. Não contornar por outro método. Publicação
FTP/Cloudflare já concluída; falta somente autorização para espelhar no GitHub,
além das pendências de métricas acima.
