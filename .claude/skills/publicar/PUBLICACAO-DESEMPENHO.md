# Publicação com desempenho — procedimento obrigatório do projeto

Pedido do dono em 10/09/2026: incorporar os aprendizados das oito páginas em toda
publicação, inclusive arquivo único do Claude Design. Meta: **90 ou mais no
PageSpeed em celular e desktop**. Chat somente se solicitado. Publicação já
autorizada vale para preparar, corrigir, publicar e medir novamente, sem renovar
aprovação para cada ajuste técnico reversível dentro do escopo.

## 1. Entender a fonte e preservar o contrato

- Ler CLAUDE.md, regras aplicáveis e `<slug>/REGRAS.md`. Preservar trabalho alheio.
- Confirmar slug/destino e identificar se já existe conteúdo publicado para
  guardar backup antes de substituir. Manter o arquivo original de origem.
- Distinguir bundler Claude Design (`__bundler/manifest`/`template`), HTML direto
  e WordPress. Não subir o invólucro “Bundled Page”, tela de loading ou React cru.
- Inventariar texto, ofertas, preço, links, CTAs, FAQ, menus, formulários,
  contadores, barras, embeds, fontes e imagem principal. Não inventar checkout,
  datas, vagas ou provas sociais. Informação essencial ausente pede esclarecimento;
  continuar preparação independente enquanto aguarda.
- `otimizar.py` é a entrada de build; `estatico.py` pré-renderiza o ramo bundler.
  Preservar funções necessárias em JS leve. Conferir o resultado, não presumir
  que remover React mantém acordeões, menus, formulários ou contadores.

## 2. Rastreamento e adendos

- `rastreamento.py` é a fonte única do GTM `GTM-P629X98`: carregar uma vez na
  primeira interação (scroll, mousemove, touchstart, click, keydown) ou após 5s.
  Inicializar dataLayer cedo e preservar sua fila. Não somar loaders nem inserir
  pixels diretos se o container já os fornece. Não voltar ao imediato apenas
  porque essa era a implementação do WordPress.
- Os pixels observados na configuração vigente foram `197461362094441` e
  `884049927923756`; verificar a configuração atual sem alterar IDs por inferência.
- Testar carregamento por tempo e por interação; uma instância e um `gtm.js`.
  A presença de fbq/pixel não comprova PageView recebido no Meta: distinguir
  inicialização, requisição enviada e confirmação no painel.
- Propagar parâmetros de campanha para o checkout correto, preservando parâmetros
  já existentes. Conferir target/rel, âncoras e navegação. Sem compras reais.
- Ajustar title, descrição, canonical, viewport, idioma e landmark principal
  conforme o produto. Nenhuma referência de outra página ou “Bundled Page”.
- **Não instalar chat por padrão.** Se solicitado, consultar CHAT-PAGINAS.md,
  conferir o widget correto e o prazo autorizado; testar abrir/fechar e falha do
  serviço. O precedente DRB usa 12s, mas não autoriza widget em outra página.

## 3. Preparar um build leve e visualmente fiel

- Construir localmente: `python3 otimizar.py <slug> /tmp/<build-da-tarefa>`.
  Inspecionar o HTML e os recursos produzidos antes de publicar.
- Falha de Chrome/render deve interromper o build, sem fallback silencioso para
  React. Rejeitar `__bundler_loading`/thumbnail no resultado. Ao editar JSON dentro
  de `<script>`, escapar `</script>` como `<\/script>`; HTML com `<img>` e assets
  ainda pode ser apenas um template quebrado. Confirmar DOM, título e conteúdo.
- Caso FSA: scripts do editor substituíam UUIDs válidos por caminhos `img/*.jpg`
  não incluídos. Usar os recursos realmente fornecidos. FAQ condicional precisa
  conter também as respostas antes da remoção de React; preferir details/summary
  nativo. Valores de media query congelados no snapshot devem virar CSS responsivo.
- Externalizar raster embutido, usar WebP e tamanho adequado ao maior uso entre
  desktop/celular. Não ampliar imagens nem remover conteúdo para obter nota.
- Identificar o LCP real. Imagem principal não é lazy; considerar preload e
  fetchpriority high. Evitar preloads múltiplos competindo entre si.
- Imagens abaixo da primeira tela: lazy apropriado; fundos CSS podem usar
  IntersectionObserver com antecedência e fallback sem JS. Verificar também
  a rolagem rápida. Não adiar a imagem principal nem ocultar o conteúdo da dobra.
- Reservar width/height ou aspect-ratio de logos e imagens. Fontes não são a
  única causa de CLS: o logo do ECM antigo empurrava a seção abaixo.
- Fontes: preservar família, métricas, pesos utilizados, acentos e pontuação.
  Preferir WOFF2, subconjunto compatível com o texto e recursos OpenType.
  Preload seletivo ou fonte crítica pequena embutida evita troca tardia. Não
  embutir indiscriminadamente todos os idiomas/pesos. Guardar fonte/configuração
  reproduzível e conferir texto e dimensões após a otimização.
- `desempenho.json` aplica fontes/preloads/fundos no ramo HTML direto; `reduzir.json`
  atende imagens do ramo bundler. Conferir qual ramo consome a configuração:
  criar um arquivo de configuração não prova que o build o utilizou.
- Remover apenas recursos comprovadamente órfãos, como script do editor que
  retorna 404. Não tratar scripts de compra/rastreamento como lixo pelo tamanho.
- Executar `verificar.py` e conferir visual em celular/desktop. Avisos do publisher
  não bloqueiam em modo não interativo. Corrigir defeitos introduzidos; documentar
  limites preexistentes sem reescrever conteúdo ou redesenhar silenciosamente.

## 4. Publicar e conferir a versão entregue

- Única entrada: `./publicar.sh <slug>`. Não usar FTP paralelo, workflow GitHub ou
  arquivos crus. Publicar só a slug solicitada, salvo escopo explícito maior.
- Cache Cloudflare: `limpar_cache.py` invalida prefixos com assets e queries.
  Limpar só `/slug/` deixou URLs com UTM/fbclid servindo código anterior.
  Conferir URL limpa e campanha previamente visitada; HTTP e HTML esperado.
- Se houver destino espelhado habilitado no publisher, conferir o resultado do
  espelho. Não mudar DNS, redirects ou campanhas sem necessidade e autorização.
- Testar produção: imagens/fontes, ausência de loading/erros JS, sem overflow,
  CTA e checkout, UTM, FAQ/menus/interações, tags nos dois modos. Sem enviar
  formulários reais, mensagens, conversões fictícias ou efetuar compras.

## 5. Medir, investigar e fechar

- Consultar PageSpeed via `medir.py` e PSI_API_KEY do .env sem expor credenciais.
  Medir URL pública mobile **e** desktop depois de publicar. Registrar URL,
  horário da coleta, versão, nota, LCP, TBT e CLS. Erro 500/429 não é uma nota.
- Abaixo de90: ler os audits específicos. LCP: TTFB, descoberta/download/render;
  TBT: tarefas/scripts efetivos; CLS: nós deslocados, espaço de imagens e fontes.
  Comparar antes/depois com versão e condições conhecidas. Não culpar Cloudflare
  por associação temporal; comparar HTTP, redirecionamentos, compressão e cache.
- Teste local ajuda isolar causas; não substitui PageSpeed público. Respostas
  interceptadas com gzip mal aplicado invalidam a medição. Validar que o browser
  renderizou a página esperada antes de aceitar a nota.
- Investigar variações relevantes; não escolher só a melhor rodada nem esconder
  pendências. Se uma correção muda o build, publicar e medir novamente.
- Core Web Vitals de campo acumulam28dias e podem ser da origem; não prometer
  aprovação imediata por uma nota Lighthouse. Não usar detecção de Lighthouse,
  tratamentos especiais para bots, conteúdo escondido ou remoção de funcionalidades.
- Concluir quando o desempenho medido e as funções cumprem o aceite. Registrar
  eventual bloqueio real com evidência; não afirmar nota constante garantida.
- Atualizar regras/relatório da página e conhecimento reutilizável quando houver
  aprendizado novo; commit/push apenas da tarefa. Entregar URL, notas dos dois
  dispositivos e limitações materiais. Referência histórica detalhada:
  `docs/PERFORMANCE-MIGRACAO.md`.
