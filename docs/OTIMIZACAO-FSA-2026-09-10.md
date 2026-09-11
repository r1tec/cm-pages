# FSA — imagens responsivas e fontes

Destino: https://contemmagia.com.br/fsa/.

O dono apontou desperdícios do PageSpeed e pediu concluir as melhorias sem
esperar outro comando para ações óbvias. A tarefa inclui publicação da FSA;
as demais páginas e configurações compartilhadas de analytics ficam preservadas.

## Alterações

- Subconjuntos Latin-ext das fontes originais, gerados de todo o texto e das
  nove respostas pelo `scripts/preparar-fontes-fsa.py`. As duas fontes que eram
  baixadas somavam 114.180 bytes; agora somam 2.612 bytes (sem cabeçalhos HTTP).
  Preservados caracteres presentes nas fontes, métricas e eixos variáveis.
- Capa derivada diretamente da exportação original em 640/960/1289px:
  17.298/29.470/52.852 bytes. Antes: 95.826 bytes em qualquer tela.
- Montagem de sonho/intuição em 640/960/1195px:
  22.208/43.812/70.170 bytes. Antes: 109.420 bytes.
- `estatico.py` replica `srcset` e `sizes` no preload da capa para evitar
  download duplicado. Página sem imagem responsiva mantém o preload anterior.
- Importador reproduzível: primeiro gerar fontes, depois executar
  `scripts/preparar-fsa.py` com a exportação original. Pillow, fonttools e brotli
  disponíveis no ambiente. A exportação em Downloads permanece intocada.

## Provas

- Comparação de 182 caixas de texto e geometria da capa com o build anterior em
  320, 390, 430, 899, 900, 1440 e 1920px, incluindo DPR 3 em 390 e DPR 2 em 1920:
  texto, fonte, tamanho e dimensões idênticos. Apenas uma variante da capa baixada.
- Todos os subconjuntos mantêm as métricas dos glifos e eixos variáveis originais.
- `verificar.py`: imagens e contraste aprovados. Nove imagens, nove FAQs, sete
  checkouts, UTM e `offer=alt` preservados, sem overflow, chat ou erros JavaScript.
- Conferência visual das duas imagens em 390 e 1440px. Conteúdo e FAQ funcionam
  sem JavaScript. GTM por tempo e por interação: uma requisição e inicialização.
- Lighthouse local da primeira rodada: 98 mobile, LCP 2,1s, TBT 0ms, CLS 0.
- Primeira rodada pública: 96 mobile (LCP 2,0s) e 100 desktop (LCP 0,5s), ambos
  TBT 0ms e CLS 0. Coletas UTC 11/09/2026 01:43:08 e 01:43:23. Aviso da capa
  eliminado; o desktop apontou a montagem abaixo da dobra, corrigida na rodada final.

### Rodada final pública

| Dispositivo | Coleta UTC em 11/09/2026 | Nota | LCP | TBT | CLS | Desperdício de imagens |
| --- | --- | --- | --- | --- | --- | --- |
| Celular | 01:53:17.294 | 97 | 2,1s | 0ms | 0 | 0 bytes |
| Desktop | 01:53:14.694 | 97 | 0,5s | 30ms | 0 | 0 bytes |

Relatórios completos: `/tmp/fsa-psi-mobile-detail.json` e
`/tmp/fsa-psi-desktop-detail.json`. A primeira tentativa da rodada final excedeu
o prazo de consulta; não foi tratada como nota nem como validação concluída.
Notas variam; a rodada anterior 96/100 foi preservada no registro.

Produção: montagem carregada em celular/desktop; FAQ nativo e texto sem JS;
GTM único por tempo/interação. HTML limpo e URL de campanha já visitada contêm
as variantes novas; bytes das fontes e imagens conferem com o build local.
Persistem avisos do beacon/decodificador de email da Cloudflare (JS legado e
cache), sem remover analytics nem mudar configuração da zona compartilhada.

Tempo aproximado até validação pública: 19 minutos, incluindo cerca de 6 minutos
de consultas/espera do PageSpeed. Uma correção adicional de imagem foi feita
durante a validação; nenhuma correção após declarar a entrega concluída.

Publicação exclusivamente por `./publicar.sh fsa`, com invalidação do cache da
página, arquivos e campanhas. Backup anterior em `/tmp/fsa-before-resource-optimization`.
Scripts de conferência: `/tmp/fsa-resource-check.cjs`, `/tmp/verify-fsa.cjs` e
`/tmp/fsa-final-extras.cjs`. Logs de publicação em `/tmp/fsa-resource-publish*.log`.

## Sugestão aos canônicos

Encaminhada ao agente central `bastao-core` pelo Orca, a pedido explícito do dono:
tratar defeitos/melhorias concretos no resultado entregue como continuação da
tarefa; executar ajustes reversíveis, validar e concluir no destino autorizado
sem exigir verbo ritual nem renovar aprovação. Manter os limites explícitos de
diagnóstico/plano e operações realmente novas ou sensíveis. Esclarecer manutenção
corretiva de páginas já publicadas no canônico de publicação.

Recibo `318cf876-274b-4502-a150-d9ed1517795e`: `accepted: true`, `turn_started`.
Isso comprova envio e início do turno; não comprova incorporação da sugestão.

Consumo de tokens por tarefa indisponível. Sem compras, conversões artificiais
ou confirmação de recebimento de eventos no painel Meta.
