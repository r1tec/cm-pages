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
| DRB | Pendente | — |
| ECM atual (`ecm-26`) | Pendente | — |
| GDP | Pendente | — |
| MCE | Pendente | — |
| MPG | Pendente | — |

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

ECM v1, hash agregado inicial de caminhos e conteúdo (para conferir exclusão):
`3ed2bb78f30fb3dfe44ec410097c8e378b9393a6636efa1565141ed422b99cfb`.
