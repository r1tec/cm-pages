# Lista Sites WordPress

Páginas publicadas em `lp.eduparmeggiani.com` (WordPress) e o estado da migração
para página leve em `contemmagia.com.br/<slug>`.

Atualizado em 20/09/2026. Fonte: `wp-json/wp/v2/pages` do WordPress cruzado com o
status HTTP de cada slug em `contemmagia.com.br`.

| Slug | Página | Migrada? | Onde está |
| --- | --- | --- | --- |
| `bpa` | BPA — Benzimento para Animais V2 | Sim | https://contemmagia.com.br/bpa |
| `bco` | BCO — Benzimento com Orixás V1 | Sim | https://contemmagia.com.br/bco |
| `bce` | BCE — Benzimento com Ervas V3 | Sim | https://contemmagia.com.br/bce |
| `mce` | MCE — Magia com Exu V2 | Sim | https://contemmagia.com.br/mce |
| `mpg` | MPG — Magia com Pombogira V2 | Sim | https://contemmagia.com.br/mpg |
| `gdp` | GDP — Guia de Pemba V2 | Sim | https://contemmagia.com.br/gdp |
| `drb` | DRB — Diário de Rezas e Benzimentos V3 | Sim | https://contemmagia.com.br/drb |
| `iat` | IAT — IA para Terapeutas V1 | Não | só no WordPress |
| `mpp` | MPP — Magia Prática com Pemba V1 | Não | só no WordPress |
| `t3x` | T3X — Transição 3X V1 (ON) | Não | só no WordPress |
| `wmpp-obrigado` | WMPP — Obrigado | Não | só no WordPress |
| `6-edb` | 6º Encontro das Benzedeiras (marcada DEV) | Não | só no WordPress |
| `6-edb-obrigado` | 6º Encontro das Benzedeiras — Obrigado | Não | só no WordPress |
| `drb-vsl` | DRB — VSL (variação da `drb`) | Não | só no WordPress |

Total: 14 páginas no WordPress — 7 migradas, 7 pendentes.

## Páginas que só existem em código

Não vieram do WordPress e não entram na conta acima: `bpv`, `coe`, `fsa`,
`ecm-26` (e a variação `ecm-26-v1`).

## Como manter

Toda migração de página do WordPress concluída atualiza esta lista na mesma
tarefa (passo de encerramento da skill `preparar-pagina`): muda a linha para
"Sim" com a URL e corrige o total e a data. Se o WordPress ganhar ou perder
página, revalide a lista inteira com:

```
curl -sL "https://lp.eduparmeggiani.com/wp-json/wp/v2/pages?per_page=100&_fields=slug,title,date"
```

e confira cada slug em `contemmagia.com.br/<slug>` pelo código HTTP.
