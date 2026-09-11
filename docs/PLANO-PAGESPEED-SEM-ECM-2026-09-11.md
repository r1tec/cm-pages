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
| DRB | Publicada e funcional; desktop 99/FCP 0,4s; mobile PSI pendente (500) |
| GDP | Em diagnóstico |
| MCE | Pendente |
| MPG | Pendente |
| FSA | Pendente; respeitar REGRAS.md e otimização de fontes já existente |

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
