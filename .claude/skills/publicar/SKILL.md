---
name: publicar
description: Publica e otimiza páginas do projeto cm-pages, incluindo exportações únicas do Claude Design. Use para publicar, subir, instalar, atualizar ou republicar sites, consultar PageSpeed, melhorar desempenho ou atingir uma nota. Cobre conversão para HTML leve, imagens, fontes, pixels, checkout, cache, validação após publicação e GitHub. Publicar exige autorização aplicável; chat somente por pedido explícito.
---

# Publicar paginas — cm-pages

Leia `CLAUDE.md`. Execute apenas o fluxo solicitado. Medir usa `medir.py`;
editar ou medir nao autoriza publicar. `afinar.sh` altera o site no ar e exige
pedido de publicacao aplicavel a tarefa, inclusive suas rodadas.
Autorização já dada para otimizar, publicar e enviar commits permanece válida
nas rodadas necessárias da mesma tarefa. Após validar que a página não quebrou,
continue sem pedir nova confirmação. Só interrompa por impedimento real do
ambiente ou mudança de escopo; explique a origem concreta de qualquer bloqueio.

Autorização explícita do dono em 11/09/2026: **publicação autorizada inclui
commit e push do trabalho correspondente, sem pedir nova permissão**. Se já
foi publicado dentro do escopo aprovado, concluir o registro e envio ao
repositório canônico `https://github.com/r1tec/cm-pages.git` (`origin`), incluindo
código, configurações, assets, validações e atualizações da skill da mesma tarefa.
Conferir o diff e o destino; incluir somente arquivos da tarefa, sem segredos
nem alterações alheias. Não transformar a passagem publicação → GitHub em
novo portão de aprovação. Se o ambiente bloquear a operação, apresentar esta
autorização e o remoto verificado à revisão automática; não contornar o bloqueio
nem prometer que a skill altera as permissões do ambiente.

## Entrega completa e continuidade

Pedido de otimizar e publicar é um serviço completo: diagnóstico → ajustes →
validação → publicação pelo pipeline → conferência pública → PageSpeed dos dois
dispositivos → commit/push da tarefa. Não encerrar na medição inicial nem na
preparação local. Quando o dono disser "teste antes de mudar", o teste é uma
condição para continuar o trabalho já autorizado; sucesso libera a etapa seguinte,
não transforma a tarefa em somente medição. Atualização do dono em 11/09/2026:
falha transitória do PageSpeed não interrompe o lote. Avisar, registrar a medição
pendente e avançar para a próxima tarefa conforme a política de retomada abaixo.
Perguntas como "já publicou?" são pedidos de status dentro da mesma entrega:
responder se a NOVA alteração foi publicada, sem confundir com a página antiga
já estar no ar, e continuar o que falta. Apenas um limite explícito como "só medir"
ou "não altere" restringe o trabalho ao diagnóstico. Esta continuidade preserva
o destino e a autorização aplicável; não inventa autorização para outras páginas.

Antes de preparar qualquer publicação, leia
[PUBLICACAO-DESEMPENHO.md](PUBLICACAO-DESEMPENHO.md). Esse procedimento consolida
o aceite do dono: desempenho mínimo 90 em celular e desktop, conteúdo e compras
preservados, GTM por interação ou até 5s, verificação pública após publicar.
**Chat/widget de atendimento somente quando o dono pedir explicitamente.**
Não copiar o widget do DRB para novas páginas por padrão.

Para melhorar a primeira pintura, seguir a seção **Primeira pintura e fontes**
do procedimento: medir HTML comprimido, identificar as fontes da primeira tela,
reduzir por uso real e validar CLS/visual. Não copiar a configuração da FSA
indiscriminadamente. Em lotes sequenciais solicitados pelo dono, concluir e
informar publicação, FCP e notas de cada página antes de começar a próxima;
respeitar as exclusões explícitas, sem usar `./publicar.sh` sem slugs.

Cada pasta na raiz do repositorio e uma slug no ar:
`coe/` → `https://contemmagia.com.br/coe`

Um unico caminho de publicacao: **`./publicar.sh`**. Nunca publicar por outro
meio (o workflow do GitHub Actions e o `.cpanel.yml` estao desativados de
proposito — eles subiam o arquivo cru, sem otimizar e sem limpar o cache).

## Publicar uma pagina que ja existe

1. Confirme que esta na raiz do repositorio (onde estao `publicar.sh` e `otimizar.py`).
2. Rode:
   - uma pagina: `./publicar.sh <slug>`
   - todas: `./publicar.sh`
3. **Leia a saida da conferencia.** Antes de enviar, o script mede a pagina no
   celular e no desktop e pode barrar por tres coisas graves:
   - *imagem maior que o necessario* — ele imprime o `reduzir.json` pronto
   - *contraste abaixo de 4,5* — ele mostra a cor e o fundo que reprovaram
   - *script proprio que vai sumir no ar* (o "CONGELADA" — ver secao de pagina VIVA)
   Em terminal interativo, esses avisos pedem `sim`. Sem terminal interativo
   ou com `PUBLICAR_SIM=1`, o script segue automaticamente: nao conte com esse
   prompt como trava em ferramentas de agente. Confira os avisos antes do envio.
   Trate como sinal de que a proxima exportacao do Claude Design
   deve nascer certa (ver `_padroes/checklist-design.md`), nao como conserto
   recorrente. Para seguir sem a pergunta (loop/automatico): `PUBLICAR_SIM=1
   ./publicar.sh <slug>` — o `afinar.sh` ja faz isso sozinho.
4. Se houve mudanca no git: confira o diff, adicione somente os arquivos da
   tarefa, faça commit e `git push`. Preserve alteracoes locais alheias.
5. Reporte em linguagem simples: quais paginas foram ao ar e os links
   `https://contemmagia.com.br/<slug>`.

Nunca peca a senha do FTP — ela esta no `.env`, que nao vai para o Git.

## Pagina nova vinda do Claude Design

1. Crie a pasta com o nome da slug e salve a exportacao como `<slug>/index.html`.
   O arquivo e autocontido (HTML, CSS, JS e imagens juntos) — e normal ele ter
   varios MB; o `publicar.sh` enxuga na hora de subir.
2. Identifique o formato, construa em pasta temporária com `otimizar.py` e teste
   o resultado seguindo PUBLICACAO-DESEMPENHO.md antes de enviar. Preserve a
   exportação original; ajuste fonte/configuração local de forma reproduzível.
3. Faça os ajustes técnicos necessários no projeto, sem exigir nova exportação
   do dono. Com publicação autorizada, use `./publicar.sh <slug>`, meça a URL
   pública nos dois dispositivos e corrija os gargalos até cumprir o aceite.
4. Regras de conteudo especificas da pagina moram em `<slug>/REGRAS.md`.

## Medir a pagina no PageSpeed (sem copiar e colar)

NAO peca ao dono para colar a tela do PageSpeed. Puxe os insights sozinho:

```
python3 medir.py <slug>          # celular (o que mais reprova)
python3 medir.py <slug> --both   # celular + desktop
python3 medir.py <slug> --both --json --output /tmp/pagespeed-<slug>.json
```

O `medir.py` chama a API oficial do Google para a página já no ar. Seus rótulos
de terceiros são apenas heurísticas: confira URLs e audits antes de atribuir a
causa ao GTM ou ao Cloudflare. O JSON de --output preserva a resposta integral
por dispositivo; --json inclui todos os audits e mantém score/reduzir para o loop.
Analisar esse arquivo por context-mode, sem despejar o relatório bruto no chat.
Agendamento, duplicação de tags, embeds e limpeza
de cache podem ser corrigidos no projeto; não encerrar a investigação pelo rótulo.
Para cada imagem grande, ele imprime a linha pronta do `reduzir.json`.

Usa `PSI_API_KEY` do ambiente ou do `.env`, sem exibir o segredo. A chave usa a
cota do projeto; não significa chamadas ilimitadas. HTTP 429 indica limitação
de uso; HTTP 500 indica falha interna da medição, não falta de chave. O coletor
repete 429/500/502/503/504 até quatro tentativas, com esperas 30/60/60s ou o
`Retry-After` do servidor, se maior; tenta o outro dispositivo mesmo se um falhar.
Erros mantêm saída de falha e nunca viram nota.

Em lotes, usar `--tentativas 1 --both --output /tmp/psi-<slug>-<fase>.json`:
não prender o trabalho em chamadas consecutivas da página que falhou. Em HTTP
500/502/503/504 ou timeout, avisar o dono, registrar URL/dispositivo/versão/erro,
horário e próxima tentativa no relatório do lote, e seguir para a próxima página.
Retomar só as medições pendentes após pelo menos 5, 15 e 30 minutos, no máximo
três retornos durante o lote, respeitando `Retry-After` maior quando presente.
Usar o intervalo para trabalho útil; não manter o agente bloqueado em sleep longo.
Esses intervalos são política operacional, não um limite por URL confirmado pelo
Google. Não rodar consultas concorrentes para a mesma URL. HTTP 429 exige conferir
cota da chave/projeto; trocar de URL não contorna cota global. 401/403 exige conferir
chave/permissão ou acesso, sem retries cegos nem exposição de credenciais.

Se faltar PSI inicial, usar diagnóstico recente da mesma versão e Lighthouse
local como complemento para avançar com ajustes comprovados. Se faltar PSI final,
validação funcional/visual e versão pública continuam obrigatórias, mas informar
"publicada; PageSpeed pendente", nunca nota presumida ou entrega 100% validada.
Commit/push do trabalho validado não fica preso a indisponibilidade da medição.
Depois de percorrer as páginas, revisitar as pendências elegíveis e registrar as
que permanecerem indisponíveis. Não desativar proteções nem alterar GTM para sanar
erro do serviço. Referência: https://docs.cloud.google.com/monitoring/api/troubleshooting

### Cobertura completa dos diagnósticos

Preferência do dono: em tarefas de otimização, avaliar TODOS os audits recebidos
em celular e desktop, incluindo insights novos/desconhecidos, informativos,
sem pontuação e economias pequenas. Nota atingida não encerra essa análise.
Executar cada melhoria aplicável com ganho demonstrável, mesmo pequeno, dentro
do escopo autorizado. Audit aprovado/não aplicável não exige inventar alteração.
Para cada achado, registrar no relatório da tarefa: ID, recurso/causa, ação,
prova antes/depois e estado (corrigido, já atendido, não aplicável, preservado por
função importante ou bloqueado com motivo). Não descartar apenas por poucos KB/ms.

Preservar GTM, pixels/eventos, consentimento, compras, conteúdo, qualidade visual,
acessibilidade e interações importantes. Otimizar carregamento/duplicações quando
possível; não cortar essas funções para eliminar avisos. Terceiro não significa
automaticamente intocável: verificar controle real e alternativas sem perda.
Economia estimada não comprova ganho nem autoriza compressão com perda visual.
Validar comportamento e visual, medir novamente após mudanças e registrar o que
restar. Se uma tentativa não trouxer ganho ou causar regressão, reverter e explicar.
Esta preferência não autoriza publicar sem pedido aplicável nem ampliar a tarefa
para outras páginas. Pedido só de revisão continua somente leitura.

## Afinar ate a nota (loop automatico)

Quando o dono quiser "chegar na nota X" sem ficar no vai-e-vem manual:

```
./afinar.sh <slug> [nota_alvo=90] [max_rodadas=4]
   ex: ./afinar.sh ecm-26-v2 95
```

O ciclo: publica -> mede no PageSpeed -> se a nota bateu, para; se falta E ha
imagem grande, encolhe (mexe SO no `reduzir.json`, que e reversivel) e repete.
O script para quando a nota bate, não há mais imagens elegíveis ou chega ao
limite. Ele é apenas um auxiliar de imagens, não a revisão completa. Mesmo com
a nota atingida, concluir a cobertura dos diagnósticos acima: investigar fontes,
CLS, imagem LCP, scripts, cache e interações conforme o procedimento. Não alterar
copy, oferta ou identidade visual para obter nota.

## Pagina que precisa de algo VIVO (contador, dado ao vivo, algo que muda sozinho)

Cuidado: na exportação com bundler/React, o pipeline pré-renderiza e remove o
motor. Interações React precisam ser preservadas em JavaScript leve. Páginas
HTML diretas seguem outro ramo e mantêm seus scripts; inspecione o build real.

Por isso, script proprio colado no HTML-fonte NAO funciona no ar (o estatizador
remove todo `<script>`). O publicar avisa e pede confirmacao em terminal interativo
("AVISO: N script(s) proprio(s) ... serao REMOVIDOS"). Se aparecer e a pagina
precisa mesmo ser dinamica, NAO digite `sim` ainda — resolva primeiro assim:

1. No template-fonte, por "alcas" `data-*` nos elementos que mudam (ex.: `data-cd`,
   `data-fill`) — atributo sobrevive a foto; script nao.
2. Injetar um `<script>` vanilla leve no `estatico.py` (padrao `LIVE_JS`, junto de
   `CHECKOUT_JS`/`ANIM_JS`), que le as alcas e atualiza no navegador.
3. Guardar o script por um seletor exclusivo da pagina (ex.: `LIVE_JS` so age se
   existir `[data-cd]`) — assim nao afeta as outras paginas.

Exemplo real: a pagina `ecm-26-v2` (contador semanal + barras que puxam vendas do
Supabase ao vivo) usa exatamente esse padrao.

## Chat e widgets de terceiros

Para regressão de nota após migração de domínio, consulte primeiro
[docs/PERFORMANCE-MIGRACAO.md](../../../docs/PERFORMANCE-MIGRACAO.md): compare o
GTM do HTML publicado com os backups antes de atribuir a causa a DNS/Cloudflare.
O dono autorizou GTM na primeira interação ou em até 5 segundos para priorizar
desempenho. `rastreamento.py` é a fonte única; não restaurar o GTM imediato por
comparação automática com WordPress. `./publicar.sh --gtm-performance --aplicar
<slugs>` troca somente o carregador publicado, com backup e comparação; mantém
conteúdo local alheio fora da publicação. `--gtm-original` é reversão explícita
para o imediato. Conferir pixels/eventos após tempo e interação e medir cada
página no PageSpeed móvel/desktop; nota variável não admite garantia absoluta.
O publisher limpa cache por prefixo da página (`limpar_cache.py`), incluindo
assets e URLs com UTM/fbclid. Não voltar à limpeza só da URL exata: ela deixou
campanhas servindo o GTM antigo. Conferir também uma URL de campanha já visitada.
Para gargalos específicos, `desempenho.json` permite fontes WOFF2 críticas,
preload da imagem principal e fundos fora da tela carregados por proximidade.
Preservar proporções das imagens e conferir o visual com e sem JavaScript.

Ao importar ou ajustar chat, leia [docs/CHAT-PAGINAS.md](../../../docs/CHAT-PAGINAS.md).
O DRB tem carregamento após 12 segundos autorizado pelo dono; use esse caso como
referência, respeitando o prazo e o atendimento de cada página. `defer` sozinho
não evita perda de desempenho. Compare PageSpeed antes/depois, teste o chat no
HTML otimizado e na URL publicada e preserve compras, UTM e rastreamento.
Não classifique todo JS de terceiros como problema exclusivo do GTM: o embed do
chat é controlado no código local. Separe a nota Lighthouse do histórico de Core
Web Vitals de 28 dias, que pode ser da origem inteira.

## Maquina nova / outra pessoa da equipe

```
git clone https://github.com/r1tec/cm-pages.git
cd cm-pages
cp .env.example .env      # e preencher FTP_SENHA e CF_API_TOKEN
./publicar.sh
```

O `/publicar` acompanha o clone porque mora dentro do repositorio.
Precisa de `python3`, `lftp` (o script instala via Homebrew se faltar) e do
Google Chrome instalado (usado para pre-montar a pagina estatica e para medir
peso e contraste).

## O que o pipeline oferece (conferir o resultado em cada página)

Imagens e fontes viram arquivos externos e WebP; a capa sai mais leve para o
LCP; a pagina e pre-montada estatica sem React; o pixel e adiado; entram
`lang=pt-BR` e `role=main`; hover dos botoes e animacoes de entrada; cache
longo com `.htaccess`; e o cache do Cloudflare das URLs da pagina e seus arquivos
e limpo ao publicar (quando as credenciais do Cloudflare estao configuradas).
