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
| BCE | Retomada da medição final; ver docs/OTIMIZACAO-BCE-2026-09-11.md |
| COE | Pendente |
| DRB | Pendente; manter chat existente e prazo autorizado |
| GDP | Pendente |
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
