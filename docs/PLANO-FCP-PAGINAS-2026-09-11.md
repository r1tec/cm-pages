# Aplicação sequencial do aprendizado de FCP

Autorização: pedido de 11/09/2026 para atualizar skills e aplicar em todas as
outras páginas, uma por vez, publicando e informando resultado antes da próxima.
Destino: https://contemmagia.com.br/<slug>/. FSA já entregue; ECM v1 excluída
explicitamente (`ecm-26-v1`), sem editar, reconstruir ou publicar essa pasta.

## Aceite de cada página

Tem que fazer: identificar peso/fontes reais, comparar com produção, otimizar
de forma reproduzível, preservar visual, validar compras/UTM/FAQ/rastreamento e
interações específicas, publicar pelo pipeline, limpar cache, medir mobile e
desktop (mínimo 90), registrar FCP/LCP/TBT/CLS e avisar o dono antes da próxima.

Não pode acontecer: mudar copy/oferta/identidade, substituir família, remover
acentos/caracteres dinâmicos, introduzir CLS, chat novo, perda de compras ou tags,
publicar mudanças locais alheias ainda não entregues, tocar ECM v1 ou publicar
em lote sem conferir individualmente. Erro de API não conta como nota.

## Ordem e continuidade

| Página | Estado | Resultado |
| --- | --- | --- |
| BCE | Publicada e validada | Mobile 97 / desktop 99; FCP 1,4s / 0,5s; CLS 0 |
| COE | Publicada e validada | 100 mobile/desktop; FCP 0,9s/0,5s; CLS 0 |
| DRB | Publicada e validada | Mobile 96 / desktop 99; FCP 1,8s/0,5s; CLS 0 |
| ECM atual (`ecm-26`) | Publicada e validada | Mobile 96 / desktop 98; FCP 1,9s/0,3s; CLS 0 |
| GDP | Publicada e validada | 98 mobile/desktop; FCP 1,9s/0,5s; CLS 0 |
| MCE | Publicada e validada | Mobile 96 / desktop Lighthouse público 100; FCP 2,0s/0,5s; CLS 0 |
| MPG | Publicada e validada | Mobile 97 / desktop 99; FCP 2,0s/0,7s; CLS 0 |

Skill canônica atualizada em `.claude/skills/publicar/`, na fonte original.
Aprendizado: medir HTML comprimido e fontes por uso, reduzir caracteres mantendo
famílias/métricas, priorizar só as fontes da abertura e validar CLS/visual.

Há alterações preexistentes em todas as páginas alvo e em `publicar.sh`, além
de migração de domínio em paralelo. Preservar e comparar conteúdo publicado
antes de enviar. Não incluir essas alterações alheias nos commits da tarefa.
Arquivos novos de configuração/fontes e alterações do pipeline devem ser opt-in
por página. Manter registro por página neste documento antes de continuar.

## BCE — preparação

- Produção e build da fonte local preexistente: texto e 128 caixas idênticos em
  390/1440, sem overflow. Não houve inclusão de conteúdo local diferente do ar.
- Montserrat crítica: original 37.956 → 21.880 bytes; Nunito abaixo da dobra:
  31.076 → 8.948 bytes. Fontes originais intocadas. Configuração seletiva remove
  o preload desnecessário de Nunito; Montserrat continua embutida.
- Testes: mesmas 128 caixas após reduzir fontes; seis imagens, 13 FAQs, sete
  checkouts com UTM, GTM único, sem erros, contraste aprovado. Auditoria local
  Lighthouse 92 antes/depois, CLS 0. FCP local variou 1,22–1,51s, sem afirmar
  ganho de tempo onde não foi demonstrado. Houve redução objetiva de bytes.
- As duas consultas PageSpeed anteriores à publicação retornaram erro 500 do
  Google. Aguardando medições da versão final; erro não conta como nota.
- Novo helper opt-in em `otimizar.py` preserva a configuração antiga. Testes com
  e sem opção seletiva passaram; `skill-creator/quick_validate.py` aprovou skill.
- Evidências: `/tmp/fcp-bce-before-inspect.json`, `/tmp/fcp-bce-after-inspect.json`,
  `/tmp/fcp-bce-verify-local.log`, `/tmp/fcp-bce-publish.log`.

### BCE — resultado público

Publicada pelo pipeline, espelho verificado e cache purgado. Medição final de
11/09/2026 12:57 UTC: mobile 97, FCP 1,4s, LCP 2,3s, TBT 0, CLS 0;
desktop 99, FCP/LCP 0,5s, TBT 0, CLS 0. A tentativa sem preload da fonte
embutida causou CLS 0,235 (nota 85); foi corrigida e republicada antes de seguir.
Revisão independente do helper apontou preservação de preloads não gerenciados
e documentação das dependências; ambos corrigidos e conferidos.
Coletor reutilizável: `scripts/inspecionar-fontes.cjs`, validado no build BCE.
Resultados comunicados ao dono antes da COE.

## COE

Produção inicial: mobile 89, FCP 1,7s, LCP 3,7s, CLS 0,001.
Subconjuntos por declaração original (incluindo estilo, peso e faixa Unicode),
Poppins normal crítica embutida com preload; Poppins itálica e IBM Plex Mono
externas. Nenhuma mudança no export. Mesmos 180 blocos em 390/1440, 16 imagens,
cinco FAQs, três checkouts com UTM, GTM único; teste local 100 e CLS 0.
HTML Brotli cresceu 18.138 → 34.861 bytes ao absorver fontes críticas; caminho
crítico e resultado público melhoraram. Não confundir HTML maior com página pior.
Publicada com cache limpo. Mobile público 100, FCP 0,9s, LCP 1,5s, TBT/CLS 0.
Desktop público 100, FCP/LCP 0,5s, TBT/CLS 0. Resultado comunicado antes da DRB.

O espelho preexistente falhou porque a conta passou a negar shell remoto apesar
de SFTP funcionar. Novo `espelho_sftp.py` envia para pasta temporária, confere
SHA-256 de cada arquivo, guarda backup e restaura em falha de troca. Teste de
upload e rollback passou; COE espelhada com 48 arquivos conferidos. Ajuste local
em `espelhar_edu.py` (arquivo preexistente da migração) preserva o fluxo e troca
somente o transporte de publicação. Não incluir a migração alheia no commit.

## DRB

Montserrat 37.956 → 22.352 bytes, Nunito 31.076 → 9.320 bytes. A primeira
embutida e antecipada; a segunda externa sem preload. Mesmos 160 blocos em
390/1440, cinco FAQs, sete links de compra com UTM e GTM único. Chat existente
com atraso de 12 segundos preservado. Lighthouse local 96, FCP 1,35s, CLS 0.
Referência pública: mobile 98, FCP/LCP 1,8s, TBT 0, CLS 0,017.
Resultado público: mobile 96, FCP 1,8s, LCP 2,6s; desktop 99, FCP 0,5s,
LCP 0,6s; TBT/CLS 0 nos dois. Coleta logo após purge teve FCP 2,0s e maior
latência do servidor; repetição 1,8s. Sem afirmar ganho de FCP nesta página:
o ganho comprovado foi redução das fontes e eliminação de CLS. Alternativa
externa antecipada melhorou FCP local em 0,15s, mas trouxe CLS 0,0179 com
fontes lentas; descartada, configuração final permanece a publicada embutida.
Chat público carregou uma única vez em 12.014ms. Espelho e cache concluídos.

## ECM atual

As três fontes Cera Pro originais WOFF viraram subconjuntos WOFF2: soma de
200.472 → 34.480 bytes. Pesos 400/700/800 preservados, fontes críticas embutidas
com preload. Mesmos 102 blocos em 390/1440; única diferença textual é o contador
avançando segundos. 15 imagens, nove FAQs, cinco compras com UTM e GTM único
passaram. Lighthouse local 99, FCP 1,0s, LCP 1,96s, TBT/CLS 0. Referência pública
mobile 91, FCP 1,7s, LCP 3,3s, TBT/CLS 0. ECM v1 não acessada pelo build.
Primeira coleta pública final: desktop 98, FCP 0,6s, LCP 0,7s, TBT 0,
CLS 0,008. Mobile 62, FCP 1,1s, LCP 2,3s, TBT 9.170ms, CLS 0,023; executor
Google com benchmark 116 contra 1214 da referência, execução ~60s contra ~11s.
Repetindo para investigar a divergência com Lighthouse local e referência.
Revisão independente dos helpers de fontes/bundler/SFTP concluída sem achados.
Repetição mobile: 94, FCP 1,9s, LCP 2,7s, TBT 0, CLS 0,023. Auditoria
identificou logotipo Raízes sem dimensões: a pintura antecipada revelou o salto.
Configurada reserva das dimensões intrínsecas 838×372, com altura automática.
Mesmos 102 blocos após correção; logo atrasado 2.200ms agora gera CLS 0.
Lighthouse local 99, FCP 0,91s, LCP 1,96s, CLS 0. Republicando versão estável.
Na republicação estável, a configuração compartilhada de espelhamento estava
desativada (mudança paralela); respeitada, sem reativá-la. Publicação principal
em contemmagia.com.br e purge concluídos normalmente.
Resultado estável público: mobile 96, FCP 1,9s, LCP 2,1s, TBT/CLS 0;
desktop 98, FCP 0,3s, LCP 0,5s, TBT/CLS 0. Resultado comunicado antes da GDP.
Regeneração de fontes preserva outras opções do desempenho.json, comprovado
com a reserva do logotipo. Nenhuma duplicação de arquivos ao regenerar.

## GDP

Montserrat 37.956 → 21.356 bytes; Nunito 31.076 → 10.244 bytes. Mesmos 99
blocos em 390/1440, sete imagens, quatro FAQs, sete checkouts com UTM e GTM
único. Lighthouse local 97, FCP 1,35s, LCP 2,63s, TBT/CLS 0. Referência pública
mobile 99, FCP/LCP 1,7s, TBT 0, CLS 0,015. Publicando após validação visual.
Resultado público 98 mobile/desktop; mobile FCP/LCP 1,9s, TBT 0, CLS 0;
desktop FCP 0,5s, LCP 0,6s, TBT 80ms, CLS 0. Sem afirmar ganho público de
FCP: referência 1,7s. Fontes menores e CLS eliminado. Verificação pública com
campanha passou; cache limpo. Resultado informado antes de passar à MCE.

## MCE

Montserrat 37.956 → 22.096 bytes; Nunito 31.076 → 10.100 bytes. Mesmos 126
blocos em 390/1440, três imagens, quatro FAQs, seis compras com UTM e GTM único.
Lighthouse local 95, FCP 1,05s, LCP 2,93s, TBT/CLS 0. Referência pública mobile
94, FCP 1,8s, LCP 2,8s, TBT 0, CLS 0,018. Publicando após validação visual.
Publicada e cache purgado. Mobile público 96, FCP 2,0s, LCP 2,4s, TBT/CLS 0.
FCP acima da referência; LCP e estabilidade melhoraram. Compras, FAQs, imagens
e GTM passaram em produção. Desktop: Google retornou erro 500 duas vezes;
terceira consulta em andamento. Skill reforça autorização persistente da tarefa.
Terceira consulta desktop também falhou. Fallback explícito: Lighthouse com
preset desktop diretamente na URL pública, nota 100, FCP 0,5s, LCP 0,8s,
TBT/CLS 0. Não é uma nota retornada pelo serviço PageSpeed. Resultado e origem
informados ao dono antes de iniciar MPG. Evidência:
`/tmp/fcp-mce-public-lighthouse-desktop.json`.

## MPG

Montserrat 37.956 → 22.260 bytes; Nunito 31.076 → 9.564 bytes. Mesmos 130
blocos em 390/1440, três imagens, quatro FAQs, seis compras com UTM e GTM único.
Lighthouse local 100, FCP 1,06s, LCP 1,73s, TBT/CLS 0. Referência pública mobile
93, FCP 1,7s, LCP 2,0s, TBT 0, CLS 0,141. Publicando após validação visual.
Resultado público: mobile 97, FCP/LCP 2,0s, TBT/CLS 0; desktop 99,
FCP/LCP 0,7s, TBT/CLS 0. Desktop exigiu repetição após erro 500 do Google.
FCP não caiu nesta coleta; CLS caiu de 0,141 para zero. Compras, FAQs,
imagens e GTM validados em produção. Cache limpo. Resultado informado ao dono.

GitHub: commit BCE enviado; envio do commit COE foi bloqueado pela revisão
automática, mesmo após verificar o remoto canônico `r1tec/cm-pages`. Pergunta
de autorização explícita respondida pelo dono: envio dos commits autorizado.

ECM v1, hash agregado inicial de caminhos e conteúdo (para conferir exclusão):
`3ed2bb78f30fb3dfe44ec410097c8e378b9393a6636efa1565141ed422b99cfb`.
Conferência final: hash idêntico nos 18 arquivos. Algoritmo: SHA-256 da
concatenação ordenada de caminho relativo ao projeto e bytes de cada arquivo,
sem separadores. Nenhuma edição, reconstrução ou publicação da ECM v1.

## Limites da validação

O lote preserva conteúdo e identidade existentes. O verificador ainda aponta
combinações de contraste preexistentes na ECM atual, MCE e MPG; não houve troca
de cores nesta otimização. Comparações de texto, fontes e geometria atestam
preservação, sem declarar que esses avisos de acessibilidade foram corrigidos.

## Fechamento

Sete páginas publicadas individualmente e validadas, com resultado comunicado
antes da próxima. Todas com CLS 0 e desempenho acima de 90 nos dois formatos;
MCE desktop medido por Lighthouse direto na URL pública após falhas da API.
O ganho de FCP não foi universal: COE melhorou de 1,7s para 0,9s; nas outras,
registrar as medições sem prometer melhora onde houve empate ou aumento.
Fontes menores e estabilidade foram ganhos recorrentes. Skill atualizada com
essa distinção, scripts reproduzíveis, reserva de imagens e autorização
persistente nas rodadas. ECM v1 conferida por hash e preservada.
