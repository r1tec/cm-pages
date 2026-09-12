# Piloto DRB — visita antecipada e experiência de carregamento

## Autorização e escopo

Em 12/09/2026, o dono pediu plano técnico, aplicação na DRB, publicação e nota final PageSpeed. Inclui validação pública e commit/push conforme skill publicar. Não inclui publicação em outras páginas, edição de campanhas ou compras de teste. Comparação Hotmart é somente leitura.

Preservar alterações locais preexistentes em `drb/index.html`, assets e `publicar.sh`; preferir modo restrito do publisher que troca somente o carregador no HTML publicado, com backup e comparação. O pedido atual autoriza antecipar Meta na DRB e prevalece sobre o padrão anterior de adiar todos os rastreadores.

## Explicação simples

Hoje todas as ferramentas esperam juntas. O piloto separa a função de avisar à Meta que a página foi aberta das demais ferramentas. A biblioteca do pixel começa cedo e envia uma visita a cada pixel já utilizado. Quando o GTM inicia depois, não deve repetir essa visita. Analytics, Ads, Clarity e o chat conservam sua programação. O pixel continua tendo custo de rede/processamento; precisamos medir seu custo isolado.

## Plano de execução

1. Registrar PageSpeed inicial da DRB e configuração real do GTM; analisar o relatório Hotmart enviado pelo dono.
2. Preparar antecipação por configuração exclusiva DRB, com prevenção de duplicação verificada contra o template real do GTM. Revisar o desenho antes de publicar.
3. Testar inicialização, fila, eventos posteriores e falhas; comparar conteúdo, aparência, checkout, parâmetros e chat. Nada de eventos falsos de compra ou Lead em produção.
4. Publicar somente o carregador da DRB pelo `publicar.sh`, conferir HTML público, eventos e desempenho móvel/desktop.
5. Registrar números, limites, reversão e versão enviada ao GitHub. Não declarar entrega ao painel Meta sem acesso ao Gerenciador de Eventos.

## Aceite — tem que fazer

- Iniciar coleta Meta sem gesto e sem temporizador de cinco segundos, usando os mesmos dois IDs.
- Uma emissão inicial por pixel, sem segunda emissão quando GTM carregar; preservar outros eventos e comportamento do SDK.
- Preservar configuração de consentimento existente; não acrescentar coleta de dados pessoais ou correspondência avançada.
- Demais ferramentas mantêm GTM por interação/5s; chat permanece em 12s.
- Configuração por página reproduzível no build; demais páginas mantêm saída anterior.
- Validação de pedido de rede separada de recepção/atribuição no painel Meta.
- Medir primeira pintura, conteúdo principal, bloqueio de processamento e estabilidade; meta PageSpeed ≥90 em ambos, investigar todo audit relevante. Relatar falhas da API sem inventar nota.

## Aceite — não pode acontecer

- Duplicar PageView no mesmo pixel ou bloquear Lead/outros eventos por bloquear o tipo inteiro de tag.
- Mascarar navegador ou alterar coleta só para PageSpeed; criar visitas/conversões artificiais como mecanismo de produção.
- Publicar conteúdo local alheio, mudar oferta, imagens, checkout, domínio de campanha ou tempo do chat.
- Prometer rastreamento perfeito, taxa de chegada de 100% ou ganho em vendas com base em laboratório.

## Estado

- **Entrega: piloto publicado; meta de desempenho não atingida.** Última coleta em 12/09/2026 às 18:43 UTC: celular **80**, FCP **1,9s**, LCP **4,5s**, TBT **170ms**, CLS **0**; desktop **89**, FCP **0,5s**, LCP **1,3s**, TBT **210ms**, CLS **0**. Não expandir com base nesta experiência como se ambos os aceites estivessem aprovados.
- Publicado em 12/09/2026 às 18:17 UTC pelo modo restrito oficial. HTML 249.215 → 250.946 bytes; conteúdo fora do script idêntico.
- Comando: `./publicar.sh --gtm-performance --meta-antecipado --aplicar drb`.
- Backup: `.build/gtm-meta-antecipado-backup/20260912T181745253876Z/`.
- SHA256 publicado: `ea2e93d3ec501efd80cbb737443ddfa441c380e3fd248791e131baaa27cb3e22`.
- Cache limpo por prefixo, incluindo variações de campanha. Espelhamento eduparmeggiani está desativado na configuração preexistente; não foi habilitado.
- PageSpeed inicial móvel: 98, FCP 1,8s, LCP 2,1s, TBT 0ms e CLS 0. Desktop: timeout, sem nota. Artefato `/tmp/psi-drb-pixel-antes.json`.
- Primeira medição publicada: móvel 84, FCP 1,3s, LCP 4,3s, TBT 100ms, CLS 0; desktop HTTP500. `/tmp/psi-drb-pixel-final.json`.
- Ajuste seguinte: moveu o preload existente de `diario.webp` para a primeira posição do head, antes da fonte inline. Publicado às 18:25 UTC, mesmo tamanho e conteúdo. Backup `.build/gtm-meta-antecipado-backup/20260912T182556047588Z/`, hash `15c9fdf2e2c2a1d4bb52c3aff9cf066cfef9f6bf2cb37e8da5b39bc3a9c7e5d5`.
- Após esse ajuste: móvel 80, FCP 1,3s, LCP 4,3s, TBT 240ms, CLS 0; desktop 97, FCP 0,6s, LCP 1,2s, TBT 70ms, CLS 0. `/tmp/psi-drb-pixel-preload-final.json`. Não houve melhora medida de LCP; variação de CPU não comprova piora causada pela posição do preload.
- O preload da imagem foi restaurado à posição original em 18:42 UTC por não demonstrar ganho. Versão final volta ao hash `ea2e93d3ec501efd80cbb737443ddfa441c380e3fd248791e131baaa27cb3e22`: somente Meta antecipada. Medição de entrega: `/tmp/psi-drb-pixel-entrega.json`.
- Duas alternativas de fonte foram testadas LOCALMENTE e descartadas: remover o preload duplicado introduziu CLS 0,01778; mover @font-face para cedo e aquecer via Font Loading API recuperou CLS 0, mas não trouxe ganho temporal geral e economizou apenas 44 bytes em Brotli. Fonte, preload e CSS publicados permanecem originais.

## Implementação e limites do piloto

`drb/rastreamento.json` habilita o modo somente nesta página. `meta-pageview-antecipado.js` mantém o bootstrap oficial do SDK (fila/callMethod/aliases), inicia os dois pixels atuais e seus PageViews. Preserva a configuração pública existente de consentimento e identificação do template. Não acrescenta dados pessoais ou matching avançado.

O adaptador suprime apenas a primeira repetição equivalente por pixel de `init` vazio e `trackSingle(id, 'PageView', {})` sem eventID. Outros eventos, parâmetros adicionais e PageViews posteriores continuam passando. Se já existir `fbq`/`_fbq`, não sobrescreve nem antecipa uma instalação alheia. O GTM mantém seu controle de IDs e seus eventos posteriores.

**É adaptação temporária ao contrato GTM v28, tags 5/34; não é deduplicação fornecida pela Meta.** Mudança dessas tags exige revalidar o piloto. A solução duradoura preferível é uma exceção de disparo dessas duas tags condicionada à flag DRB, dentro do GTM. Bloquear o tipo inteiro seria incorreto: Lead compartilha o template.

O GTM insere uma segunda referência à biblioteca; nos testes normais houve um único pedido de rede observado para `fbevents.js`. No teste de falha da primeira requisição, houve nova tentativa pelo GTM e a fila foi processada. Isso não comprova recuperação de um pedido de evento perdido depois de a biblioteca já ter carregado.

## Provas de comportamento

- Testes locais `node scripts/testar-meta-antecipado.cjs`: ordem SDK/GTM invertida, fila de biblioteca indisponível, bootstrap repetido, fbq preexistente, init e PageView únicos, demais comandos e visitas posteriores preservados. Sem rede/conversões fictícias nesses testes.
- SDK e GTM reais, quatro cenários (normal, toque, biblioteca lenta e falha inicial): dois init e dois PageViews iniciais na fila, pixels corretos registrados, fila final vazia e nenhum PageView adicional ao carregar GTM; nenhum erro JS. `/tmp/drb-piloto-final-browser.json`.
- Build temporário contém exatamente um piloto e exclui `rastreamento.json` dos arquivos públicos. `verificar.py` aprovou imagens e contraste.
- Prévia versus referência: texto e links idênticos; capturas móveis visualmente iguais; sem overflow também em desktop. Normalizador idempotente e reversão byte a byte confirmados.
- Produção: biblioteca Meta solicitada em 114ms no teste móvel e 83ms no desktop; GTM em 5,12s/5,09s; chat em 12,01s/12,02s. Tempos locais sem limitação de rede/CPU, não equivalem ao PageSpeed. `/tmp/drb-piloto-publico-browser.json`.
- Os pixels configuram bloqueio de `HeadlessChrome`, identificação do navegador automatizado. Não houve comprovação de recebimento no Gerenciador de Eventos nem de aumento de LPV atribuído. Não mascaramos o navegador nem criamos conversões falsas.
- Revisão independente sênior: nenhum bloqueador após os quatro cenários; entrega Meta e PageSpeed permanecem aceites separados.
- URL de campanha pública retorna 200 e coincide com o HTML publicado após excluir apenas o beacon adicionado pelo Cloudflare e a quebra de linha associada. Os sete links preservam UTM; os cinco FAQs abrem/fecham; nenhum erro JS. `/tmp/drb-publico-funcional.json`. O primeiro teste de igualdade bruta identificou corretamente essa inserção na borda; não era conteúdo divergente nem cache antigo.
- Chat abre e fecha na versão pública, sem preenchimento ou envio de mensagem. Capturas em `/tmp/drb-publico-chat-aberto.png` e `/tmp/drb-publico-funcional.png`.

## Experiência real versus nota composta

Lighthouse local, documento interceptado e mesmos limites de CPU/rede: anterior 100, atual 87. Essa diferença não significa que todo o processamento foi acrescentado: em janela comum de 0–14s, a soma do trecho de tarefas acima de 50ms foi 531,5ms antes e 552,9ms depois. O TBT oficial 0→532ms usa janelas diferentes. A diferença de 21,4ms na janela comum também não pode ser atribuída inteiramente ao pixel em uma única rodada.

São observações de laboratório, não medições de interação humana nem INP de usuários. O documento interceptado não mede a transferência CDN do HTML. A concorrência de rede vista no PSI permanece custo real; não desconsiderar o LCP móvel de 4,3s só porque o processamento total é semelhante. Relatórios locais: `/tmp/drb-local-lighthouse/RELATORIO.md` e `FONT-WARM-RELATORIO.md`.

## Decisão após os testes

O dono autorizou publicar o piloto para testar. Ele permanece somente na DRB, com o desempenho medido exposto e sem declaração de otimização plenamente aprovada. A coleta do navegador começa cedo; não foi demonstrado que a taxa de LPV da campanha melhorou. A espera artificial saiu do pixel, mas sua biblioteca tem custo de rede e execução que não desaparece ao separar as ferramentas.

O caminho para uma próxima fase é confirmar recepção real no Gerenciador de Eventos e avaliar a experiência de tráfego real. A configuração definitiva no GTM pode substituir o adaptador temporário; não há prova de que apenas essa substituição elimine o peso do SDK. Outra arquitetura de envio pelo servidor exigiria desenho, dados reais e validação próprios, não é uma correção automática oferecida nesta entrega.

Cobertura dos 47 audits por dispositivo em `docs/DRB-PIXEL-AUDITS-2026-09-12.md`. Cópias locais das provas principais preservadas em `.build/diagnostico-drb-20260912/` (fora do Git). Nenhum ganho adicional verificável foi encontrado que preserve rastreamento e visual; não remover SDK ou observação do Cloudflare apenas para elevar a nota. Só a categoria performance foi solicitada ao PSI.

## Reversão

Definir `meta_pageview_antecipado` como `false` em `drb/rastreamento.json` e executar `./publicar.sh --gtm-performance --aplicar drb`. O normalizador substitui o script completo pelo carregador anterior de interação/5s. Conferir o HTML público e os parâmetros após a reversão. Não publicar a fonte HTML local alheia para reverter este piloto.

Para desfazer uma operação exata do modo restrito, `./publicar.sh --gtm-performance --restaurar-backup=.build/<pasta>/<data> --aplicar drb` exige que o HTML remoto ainda seja idêntico ao `drb.after.html` daquele backup, antes de restaurar `drb.before.html`. Rejeita caminho fora de `.build` e mudança remota posterior. Usar `--restaurar-backup=...` com valor junto do argumento para o encaminhamento correto pelo shell do publicador.
