# Chat nas páginas estáticas

## DRB — 10/09/2026

Pedido: corrigir a perda de desempenho após importar o chat, testar e publicar.
Autorização: atraso de até 15 segundos e publicação nesta tarefa. Demais páginas
ficam para pedido posterior.

Plano: consultar PageSpeed com a PSI_API_KEY local; tirar o chat do carregamento
inicial; testar a versão otimizada em celular e desktop; publicar somente DRB;
repetir PageSpeed e a abertura/fechamento do chat na URL pública.

Aceite: carregar uma única instância do mesmo atendimento, iniciar o download
após 12 segundos desde a navegação, manter checkout/UTM e acordeão funcionando,
preservar o conteúdo, não atrasar GTM/pixels. Falha do fornecedor não pode impedir
leitura ou compra. Tempo de download do fornecedor varia com a conexão.

## Padrão para próximas páginas

- Origem: WordPress `https://crhishmxlb.wpdns.site/drb/`.
- Loader público: `https://widgets.leadconnectorhq.com/loader.js`.
- Atendimento do DRB: `6a0dae4cfc28868f0a82f97d`. Conferir o identificador da
  página original antes de reutilizar em outra campanha.
- Preservar `data-resources-url="https://beta.leadconnectorhq.com/chat-widget/loader.js"`
  do embed original. Esse atributo não é o endereço do script a baixar.
- Não copiar `type="litespeed/javascript"` nem a URL de cache do WordPress.
- `defer` sozinho não evita a disputa por rede/processador durante a abertura.
  Usar o carregador `#cm-chat-loader` do DRB, com espera real de 12 segundos,
  script assíncrono e proteção contra duplicação. Não antecipar no scroll/toque:
  isso faria o chat disputar recursos com a primeira interação do visitante.
- O atraso deve valer para todos os visitantes, sem detecção de PageSpeed.
  Não atrasar compras, pixels ou GTM junto com o chat.
- Testar o HTML **otimizado**. Páginas WordPress estáticas preservam scripts;
  exportações React passam por `estatico.py`, que os remove. Nessas exportações,
  integrar explicitamente o carregador ao estágio estático, restrito à página.
- Conferir zero requisições do chat antes do prazo, uma instância depois,
  abertura/fechamento em desktop e celular e compra funcionando com chat bloqueado.
- Publicar exclusivamente por `./publicar.sh <slug>`, com autorização aplicável.
  Medir PageSpeed antes/depois usando `medir.py` e a chave local, sem exibi-la.
  Consultar os audits por URL: nem todo JavaScript de terceiro é GTM/Facebook;
  o momento de carregar nosso embed pode ser corrigido aqui.
- Core Web Vitals usa histórico de 28 dias e pode representar a origem inteira.
  Separar esse histórico da nota Lighthouse atual; não prometer aprovação imediata.

## Evidências

Antes, API PageSpeed: celular 61 (LCP 7,1s, TBT 510ms, CLS 0,017);
desktop 84 (LCP 2,3s, TBT 160ms, CLS 0,03). São amostras, não médias.
Primeira publicação (só atraso): celular 57, desktop 69; repetição celular 68.
Audits confirmaram zero requisições LeadConnector no carregamento inicial,
mas ainda apontaram scripts Google/Facebook e carregamento antecipado de imagens.
Não atribuir toda oscilação da nota ao chat nem escolher só a melhor amostra.

Segunda correção: cinco fundos de imagem abaixo da primeira dobra usam
IntersectionObserver, com antecedência de 800px à rolagem. A capa continua
prioritária. Sem JavaScript ou sem suporte ao observer, mantém-se o CSS original;
falha na inicialização remove o bloqueio. Não alterar dimensões ou esconder texto.
Os quatro posters de vídeo e os scripts de rastreamento foram preservados.

Testes locais: mesmos fundos, dimensões e posicionamento em 390px e 1440px,
com e sem JavaScript; nenhum download dos cinco fundos antes da aproximação.
Chat: download começa em 12s, uma instância, abre/fecha; sete links com UTM e
cinco itens de FAQ funcionam inclusive com o fornecedor bloqueado. Após a primeira
publicação, chat pronto em 13,0s no celular e 14,2s no desktop, sem erros de JS.

Skill publicar: referência adicionada; frontmatter e link conferidos. Validador
Python padrão indisponível neste ambiente por ausência do módulo PyYAML.
Consumo de tokens não disponível; não estimado.

### Resultado final e limite da correção

Segunda publicação e cache limpo; HTML público idêntico ao `.build/drb/index.html`.
Chat no ar: início do download em 12,0s; pronto em 13,3s (desktop) e 12,8s
(celular). Abertura/fechamento, UTM nos sete links, cinco itens do FAQ e ausência
de erros JS aprovados; compra/FAQ preservados com o fornecedor bloqueado.

PageSpeed após a segunda publicação (duas rodadas, sem selecionar a melhor):

| Rodada | Celular | LCP | TBT | Desktop | LCP | TBT |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 69 | 8,7s | 260ms | 67 | 1,2s | 3650ms |
| 2 | 49 | 6,8s | 1730ms | 87 | 1,4s | 240ms |

CLS zero nas duas estratégias/rodadas. Auditoria de rede confirmou ausência do
chat e dos cinco fundos no carregamento inicial. As notas continuam oscilando;
**não houve recuperação consistente do PageSpeed** e não declarar problema
integralmente resolvido. Os long tasks finais apontam Facebook, Google/Ads e
Clarity. Não repetir medições indefinidamente buscando uma nota verde.

Diagnóstico local comparável, cache desativado, CPU 4x, rede 1,6Mbps/150ms,
mesma URL, janela anterior ao chat (11s): com rastreamento, LCP 1536ms e soma
de bloqueios acima de 50ms de 644ms; com tags de marketing bloqueadas apenas
nesse navegador de teste, LCP 1328ms e bloqueios 23ms. Esta é uma medição de
diagnóstico, não nota Lighthouse nem estatística de visitantes. O site público
continua com todas as tags.

Inventário público para próxima investigação no GTM:
`GTM-P629X98` (uma inclusão), GA `G-CGY4CM7NXE`, Ads `AW-956533053`,
pixels Facebook `197461362094441` e `884049927923756`, Clarity `hvofrp21xv`.
Dois pixels não provam duplicação indevida: validar a finalidade de cada um
antes de remover ou mudar disparos. O próximo trabalho é auditar essas tags e
seus gatilhos no GTM, preservando eventos/campanhas; não mascarar a nota atrasando
todo o rastreamento nem tratar permissão de atraso do chat como permissão para
atrasar pixels. Core Web Vitals histórico permanece separado desta correção.
