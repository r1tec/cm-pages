# BCE — entrega completa após diagnóstico PageSpeed

Autorização atual: dono pediu aplicar otimizações e publicar a BCE, preservando
GTM e funções importantes, incluindo melhorias pequenas. Decisão mais recente:
em falha transitória do PageSpeed, avisar, seguir para próxima tarefa e retomar
após intervalo (ver plano do lote sem ECM). Teste inicial já concluído: 11/09/2026 14:08 UTC, mobile
96 (FCP 1,4s, LCP 2,4s, TBT/CLS zero), desktop 100 (FCP 0,4s, LCP 0,5s,
TBT/CLS zero). Relatório recebido pelo dono às 14:14 UTC: 94/100, mobile LCP
2,9s; mesmos recursos otimizados. Não houve nova publicação nessa medição.

## Aceite

Tem que fazer: avaliar os 47 audits por dispositivo, aplicar melhorias viáveis,
validar visual/conteúdo/compras/FAQ/GTM, publicar somente BCE pelo pipeline,
conferir produção e medir novamente, registrar ressalvas e entregar no GitHub.

Não pode acontecer: remover rastreamento ou conteúdo para nota; publicar edições
locais alheias; declarar entregue com apenas teste inicial; prosseguir após falha
de PageSpeed sem registrar pendência; alterar páginas fora do lote autorizado.

## Estado

Segunda rodada publicada e validada; medição pública final em andamento.
Diagnóstico integral inicial: `/tmp/pagespeed-bce-nova-skill.json`.
Edições locais preexistentes em bce/index.html e depoimentos preservadas: conteúdo
do build comparado com produção em 390/1440px (textos, sete compras/UTM, quatro
vídeos e 13 FAQs iguais). Esses arquivos alheios não entram no commit da tarefa.
Consumo de tokens por tarefa: indisponível no ambiente.

## Implementação e provas locais

- Roboto: 43.136 → 23.488 bytes, todos os caracteres do texto incluindo FAQ,
  maiúsculas/minúsculas, preços e fallback. Métricas e cobertura verificadas;
  original preservada, gerador `scripts/preparar-roboto-bce.py`.
- Quatro imagens de ervas com variantes 250/400px e logo 430/739px. `sizes`
  corresponde ao layout, arquivo maior preservado para telas densas. Nomes
  por hash evitam reuso de versão antiga. Proporção original explícita evita
  deslocamento por arredondamento da altura do bitmap menor.
- Compressão adicional de 01.webp (39.420 → 31.152 bytes a 400px, 15.954 a 250px)
  e foto principal (77.704 → 76.398). Inspeção visual comparativa aprovada.
- Preload da foto principal movido para início do head e atualizado para a nova
  URL, removendo o preload antigo para impedir download duplicado.
- 307 nós de texto com caixas idênticas em 320/360/390/430/767/768/1024/1440px;
  proporções iguais, sem overflow ou erro JS. FAQs testadas e todas as imagens
  carregadas após rolagem. GTM observado uma vez por tempo e por interação;
  execução de tags externas interceptada no teste local, sem conversões fictícias.
- Sete CTAs reais `pay.contemmagia.com.br/c/bce` e propagação de UTM verificados
  separadamente em 390/1440; o verificador inicial tinha filtro de domínio antigo,
  corrigido antes de considerar compras aprovadas.
- `verificar.py`: imagens e contraste aprovados. Nove testes automatizados
  passaram; skill validada. Provas: `/tmp/bce-completo-validacao.json`,
  `/tmp/bce-completo-preflight-{public,local}-{390,1440}.png`.
- Lighthouse local móvel: antes 91, FCP 1,5s, LCP 3,5s, TBT/CLS zero. Primeiro
  candidato 90/LCP 3,6s tinha preload duplicado, corrigido. Final 91, FCP 1,5s,
  LCP 3,4s, TBT/CLS zero. Economia de bytes comprovada; não atribuir a oscilação
  de 0,1s a ganho causal. JSONs em `/tmp/bce-completo-lh-{before,final}.json`.

## Cobertura dos diagnósticos iniciais

Todos os 47 audits de cada dispositivo foram inspecionados, incluindo valores
de savings em audits aprovados. Fora de imagens, savings de CSS/JS/servidor eram
zero; tabelas de CSS/JS não utilizados vazias. Não remover código por suposição.

| Audit/achado | Ação e estado antes da medição final |
| --- | --- |
| image-delivery-insight | Variantes e compressões aplicadas; maior resolução preservada; validar economia pública. |
| network-dependency-tree-insight | Roboto reduzida; preload da foto atualizado/antecipado; Nunito já reduzida e sem preload. Sem candidatos de preconnect. |
| lcp-breakdown-insight / LCP / FCP / speed-index / interactive | Foto principal e fontes tratadas; métricas finais pendentes. Montserrat crítica embutida e antecipada preservada para evitar CLS comprovado na entrega anterior. |
| forced-reflow-insight / max-potential-fid | Desktop mostrou 108,8ms sem atribuição; mobile sem ocorrência. Sem leituras geométricas no JS próprio da página; não há causa segura para editar. Reavaliar coleta final. |
| cache-insight / legacy-javascript-insight | Relatório do dono apontou beacon Cloudflare (4/11KiB). Arquivo hospedado pelo provedor; não remover medição nem alterar GTM. Cache próprio e versão verificados. |
| third-parties-insight | Rastreamento e medição preservados. Verificados loader único e prazo do GTM. |
| Demais audits aprovados/informativos | Revisados: CSS/JS sem economias indicadas, documento sem redirecionamento ou bloqueio, imagens dimensionadas, fontes com display adequado, TBT/CLS zero. Dados de rede/DOM/tarefas/screenshots sustentam diagnóstico; não requerem corte de conteúdo. |
| Não aplicáveis | INP sem interação medida, layout-shifts sem deslocamentos, user-timings e animações não compostas sem achados. Não inventar correção. |

## Primeira publicação e refinamento

Publicação pelo pipeline concluída, cache limpo por prefixo com assets/queries.
Espelho preexistente desativado, mantido assim. Produção validada em 390/1440:
mesmo conteúdo, sete compras/UTM, quatro vídeos, 13 FAQs, imagens carregadas e
zero erros. Foto servida pela nova URL e apenas um preload, apontando para ela.

PageSpeed 14:33:57 UTC: mobile 97, FCP 1,1s, LCP 2,4s, TBT/CLS zero.
Desktop 14:34:15 UTC: 100, FCP 0,3s, LCP 0,5s, TBT/CLS zero. Sem erros.
47 audits por dispositivo preservados em `/tmp/pagespeed-bce-completo-rodada1.json`.
Entrega de imagens passou de 62/57 KiB estimados para 25/10 KiB (mobile/desktop).
Roboto público agora 24.288 bytes transferidos, contra aproximadamente 44KB.

Ainda havia sugestão de compressão em 01.webp e na foto principal. Segunda rodada
testa q55/q60 respectivamente, mantendo resolução e fontes originais. Parte do
aviso móvel de tamanho de 400px para exibição de 250px será preservada: a tela de
maior densidade usa a variante maior, não se reduz nitidez para eliminar o aviso.

Segunda compressão aprovada visualmente: alecrim 25.806 bytes a 400px e 14.050
a 250px; foto principal 71.298. Republicação pelo pipeline e purge concluídos.
Build enviado idêntico ao validado (SHA-256 do HTML):
`0ae30a8ce76b0194b999b50ab24a52652d8ca16c4697df0301a09521d38b10cb`.
Verificação pública final passou em 390/1440: sete CTAs com UTM, 13 FAQs
funcionais, quatro vídeos preservados, imagens carregadas, zero erro JS/overflow
e preload único da nova foto. Originais das imagens não foram alterados.
