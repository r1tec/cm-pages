# Expansão do chat e Meta antecipada — 12/09/2026

## Escopo e resultado

Pedido: aplicar à MCE a antecipação Meta da DRB; levar chat e antecipação a BCE,
BPV, MPG, COE e GDP, preservando atendimento próprio. Confirmações posteriores:
COE sem chat; BPV está no Lovable e nesta etapa recebe somente plano de migração
em `docs/PLANO-BPV-MIGRACAO-2026-09-12.md`. ECM/FSA não foram editadas/publicadas.

Publicadas MCE, BCE, MPG, COE e GDP pelo `publicar.sh --build .build/<slug> <slug>`,
com cache limpo por página/campanhas. Alterações locais preexistentes dessas
páginas preservadas e incluídas na publicação. Espelhamento Edu continua desativado.

| Página | Atendimento |
| --- | --- |
| MCE | `6a0e1e3957ddb4d64b351981` — mantido |
| BCE | `6a0dfb5754c6962db0f8155c` |
| MPG | `6a0e1e472fd1d186c5003270` |
| GDP | `6a0e1b99605fc07a5102e06c` |
| COE | Sem chat, por confirmação do dono |

BCE/MPG/GDP: identificadores e resources URL conferidos no embed das respectivas
páginas originais `https://crhishmxlb.wpdns.site/<slug>/`. Mantida resources URL
`https://beta.leadconnectorhq.com/chat-widget/loader.js`. Os três carregadores
são idênticos à MCE salvo ID. Ícone local WhatsApp, selo visual, animação com pausa
quando aberto/aba oculta/movimento reduzido e atrasos 5/7/10 segundos preservados.

Os cinco opt-ins usam `rastreamento.json`. Para a COE, o caminho de exportação
React em `otimizar.py` agora aplica a mesma normalização após gerar HTML estático
e não copia a configuração para o servidor. São as únicas duas alterações no
pipeline desta tarefa; demais mudanças preexistentes nele ficam fora do commit.

## Validação

- Testes de contrato Meta e normalização passaram: um init/PageView inicial por
  pixel antes/depois do SDK/GTM, outros eventos e visitas posteriores intactos.
- Dez cenários Chrome local, 390/1440 px: Meta antes do GTM, atendimento correto,
  instância única, abrir/fechar, WhatsApp persistente, selo removido, sem imagens
  quebradas na região carregada e sem erros JS. Links de compra com UTM: MCE 6,
  BCE 7, MPG 6, GDP 7, COE 3.
- Com o fornecedor do chat bloqueado, links de compra e parâmetros preservados
  em MCE/BCE/MPG/GDP; FAQ conferido separadamente por estrutura de cada página.
- Revisão independente de correção/contrato: um fechamento HTML duplicado nos
  três chats novos foi encontrado, corrigido e reconferido; nenhum achado restante.
- Publicação pública: HTTP 200 com e sem campanha, conteúdo igual ao build
  descontando exclusivamente beacon Cloudflare e espaço entre tags; ícones
  públicos idênticos aos builds. COE confirmada sem chat.

| Página | Início biblioteca Meta | Início GTM |
| --- | --- | --- |
| MCE | 32 ms | 5.035 ms |
| BCE | 52 ms | 5.054 ms |
| MPG | 93 ms | 5.095 ms |
| COE | 32 ms | 5.038 ms |
| GDP | 49 ms | 5.051 ms |

Tempos de uma navegação pública móvel por página, sem interação. Não representam
confirmação de recepção ou atribuição no painel Meta. Nenhum formulário, mensagem
ou compra foi enviado.

## Impacto medido no desempenho

| Página | Antes móvel/desktop | Depois móvel/desktop | LCP móvel depois | TBT móvel depois |
| --- | --- | --- | --- | --- |
| MCE | 96 / 100 | Indisponível | — | — |
| BCE | 96 / 100 | 78 / 95 | 4,8 s | 190 ms |
| MPG | 100 / 100 | 83 / 95 | 4,5 s | 60 ms |
| COE | 100 / 100 | 82 / 98 | 3,7 s | 300 ms |
| GDP | 98 / 100 | 83 / 96 | 4,0 s | 200 ms |

CLS zero em todas as amostras válidas dessas cinco páginas. MCE: Google retornou
HTTP 500 nos dois dispositivos, inclusive em uma retomada após medir as demais;
não há nota final válida e não houve novas tentativas repetitivas.

O resultado atende à prioridade solicitada de começar a Meta sem esperar GTM,
**não comprova ganho geral de velocidade**. As notas móveis caíram após a mudança.
Os audits mostram execução do SDK/configurações Meta na janela inicial, além do
trabalho da própria página. A antecipação tem custo, como já registrado no piloto
DRB; não suprimir o SDK, eventos ou mudar o prazo aprovado para fabricar nota alta.
As amostras não isolam causalmente toda variação de rede/renderização. Não foi
solicitada reformulação visual ou otimização completa das cinco páginas.

## Provas e limites

Scripts de conferência: `/tmp/test-rollout-chat-meta.cjs` e
`/tmp/verify-rollout-public.cjs`; screenshots `/tmp/rollout-<slug>-*.png`;
respostas integrais PSI `/tmp/rollout-antes-*.json` e `/tmp/rollout-depois-*.json`.
Inventário BPV, testes e JSONs PSI também preservados fora do Git em
`.build/diagnostico-expansao-20260912/`.
O verificador público precisou corrigir duas questões do próprio teste: ignorar
um espaço injetado pelo Cloudflare e ler `Response.status` como propriedade.
Ambas resolvidas antes de declarar validação pública concluída.

Retomada/reversão: desativar o opt-in de uma página, preparar e publicar somente
essa página. Não restaurar arquivos inteiros antigos sobre mudanças posteriores.
Chat pode permanecer independentemente da configuração Meta.

Consumo real de tokens indisponível. Uma lente independente utilizada.
