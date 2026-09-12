# Hotmart: nota de laboratório e experiência percebida

Análise somente leitura do [relatório indicado pelo dono](https://pagespeed.web.dev/analysis/https-pay-hotmart-com-L103859537W/bsnlp58wna?form_factor=mobile), coletado em 12/09/2026 às 18:02 UTC. Não houve pagamento, preenchimento ou envio no checkout.

## Resultado

| Medida | Celular | Desktop |
|---|---:|---:|
| Nota Lighthouse | 25 | 39 |
| Primeiro conteúdo | 13,6s | 1,4s |
| Maior conteúdo | 34,5s | 6,3s |
| Bloqueio acumulado do processamento | 4.140ms | 1.850ms |
| Instabilidade visual | 0,016 | 0,009 |

No celular, o elemento escolhido para LCP é **o texto do aviso de cookies**, não o formulário de pagamento. Um elemento grande que aparece tarde pode dominar essa métrica mesmo quando parte útil já apareceu. O relatório também mostra custo real: cerca de 5,23MiB transferidos e 11,4s de trabalho da thread principal. Aplicação, iframe de pagamento, tags e segurança contribuem. Não se pode tratar todo esse trabalho como descartável.

## O que os usuários reais mostram

A URL não tem amostra própria suficiente; o painel usa a origem inteira `pay.hotmart.com`, de 13/08 a 09/09/2026, percentil 75. Não atribuir esses números ao checkout deste produto individualmente.

| Campo da origem | Celular | Desktop |
|---|---:|---:|
| Maior conteúdo (LCP) | 2,1s | 1,5s |
| Resposta às interações (INP) | 298ms | 108ms |
| Instabilidade visual (CLS) | 0,01 | 0,08 |
| Core Web Vitals | Reprovado | Aprovado |

A origem tem abertura rápida para muitos visitantes; no celular, a resposta às interações ainda precisa melhorar. Isso sustenta a possibilidade de percepção rápida com nota baixa, mas não prova excelência para todos nem que a nota esteja errada.

## Aprendizado aplicado à DRB

Usar quatro critérios juntos: conteúdo útil aparece cedo; toque e rolagem respondem; layout não salta; visita e ações importantes são registradas corretamente. Manter PageSpeed como diagnóstico e comparar com dados de usuários e conversão, quando disponíveis. Não ganhar nota atrasando funções comerciais essenciais nem ignorar trabalho pesado porque a primeira tela parece pronta.

O piloto DRB inicia Meta cedo, conserva ferramentas secundárias adiadas e mede o custo real dessa separação. O aviso de cookies da Hotmart ilustra por que conferir o elemento LCP é necessário antes de interpretar seu número como “tempo até poder comprar”.

Artefatos integrais: `/tmp/hotmart-lighthouse-mobile.json`, `/tmp/hotmart-lighthouse-desktop.json`, `/tmp/hotmart-psi-visible.txt`. Diagnóstico detalhado: `/tmp/hotmart-performance-diagnostico.md`.
