---
name: publicar
description: Publica e otimiza páginas do projeto cm-pages, incluindo exportações únicas do Claude Design. Use para publicar, subir, instalar, atualizar ou republicar sites, consultar PageSpeed, melhorar desempenho ou atingir uma nota. Cobre conversão para HTML leve, imagens, fontes, pixels, checkout, cache, validação após publicação e GitHub. Publicar exige autorização aplicável; chat somente por pedido explícito.
---

# Publicar paginas — cm-pages

Leia `CLAUDE.md`. Execute apenas o fluxo solicitado. Medir usa `medir.py`;
editar ou medir nao autoriza publicar. `afinar.sh` altera o site no ar e exige
pedido de publicacao aplicavel a tarefa, inclusive suas rodadas.

Antes de preparar qualquer publicação, leia
[PUBLICACAO-DESEMPENHO.md](PUBLICACAO-DESEMPENHO.md). Esse procedimento consolida
o aceite do dono: desempenho mínimo 90 em celular e desktop, conteúdo e compras
preservados, GTM por interação ou até 5s, verificação pública após publicar.
**Chat/widget de atendimento somente quando o dono pedir explicitamente.**
Não copiar o widget do DRB para novas páginas por padrão.

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
```

O `medir.py` chama a API oficial do Google para a página já no ar. Seus rótulos
de terceiros são apenas heurísticas: confira URLs e audits antes de atribuir a
causa ao GTM ou ao Cloudflare. Agendamento, duplicação de tags, embeds e limpeza
de cache podem ser corrigidos no projeto; não encerrar a investigação pelo rótulo.
Para cada imagem grande, ele imprime a linha pronta do `reduzir.json`.

Precisa de uma chave gratis no `.env` (`PSI_API_KEY`) — sem ela o Google recusa
por excesso de uso (erro 429). Como criar: ver o comentario no `.env.example`.

## Afinar ate a nota (loop automatico)

Quando o dono quiser "chegar na nota X" sem ficar no vai-e-vem manual:

```
./afinar.sh <slug> [nota_alvo=90] [max_rodadas=4]
   ex: ./afinar.sh ecm-26-v2 95
```

O ciclo: publica -> mede no PageSpeed -> se a nota bateu, para; se falta E ha
imagem grande, encolhe (mexe SO no `reduzir.json`, que e reversivel) e repete.
O script para quando a nota bate, não há mais imagens elegíveis ou chega ao
limite. Isso não encerra a tarefa se o aceite não foi cumprido: investigar fontes,
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
