---
name: publicar
description: Publica paginas do repositorio cm-pages na hospedagem da Contem Magia e espelha no GitHub. Use SEMPRE que o usuario pedir para publicar, subir, colocar no ar, atualizar ou republicar uma pagina, disser "publica o coe", "sobe essa pagina", "poe no ar", "atualiza a pagina X", ou quando uma pagina nova exportada do Claude Design entrar no repositorio e precisar ir para a hospedagem. Cobre tambem a conferencia de peso e contraste antes de subir e a nova pagina a partir de uma exportacao do Claude Design. Cobre ainda MEDIR a pagina no PageSpeed sozinho (medir.py — puxa os insights do Google, sem o dono copiar e colar) e AFINAR ate a nota de performance em loop (afinar.sh — publica, mede, encolhe imagem, repete). Use quando o dono pedir para "otimizar", "melhorar a nota", "testar no pagespeed", "chegar em X de performance", "ver os insights", ou variacoes.
---

# Publicar paginas — cm-pages

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
   Achando qualquer uma, a publicacao **para e pede confirmacao**: so sobe se
   digitar `sim`. Trate como sinal de que a proxima exportacao do Claude Design
   deve nascer certa (ver `_padroes/checklist-design.md`), nao como conserto
   recorrente. Para seguir sem a pergunta (loop/automatico): `PUBLICAR_SIM=1
   ./publicar.sh <slug>` — o `afinar.sh` ja faz isso sozinho.
4. Se houve mudanca no git: `git add -A`, commit e `git push`.
5. Reporte em linguagem simples: quais paginas foram ao ar e os links
   `https://contemmagia.com.br/<slug>`.

Nunca peca a senha do FTP — ela esta no `.env`, que nao vai para o Git.

## Pagina nova vinda do Claude Design

1. Crie a pasta com o nome da slug e salve a exportacao como `<slug>/index.html`.
   O arquivo e autocontido (HTML, CSS, JS e imagens juntos) — e normal ele ter
   varios MB; o `publicar.sh` enxuga na hora de subir.
2. Rode `./publicar.sh <slug>`.
3. Se a conferencia reclamar, corrija de preferencia **no Claude Design** e
   reexporte. So use `<slug>/reduzir.json` / `<slug>/cores.json` quando
   reexportar nao for viavel — sao remendos locais, e a saida do `verificar.py`
   ja entrega o conteudo pronto para colar.
4. Regras de conteudo especificas da pagina moram em `<slug>/REGRAS.md`.

## Medir a pagina no PageSpeed (sem copiar e colar)

NAO peca ao dono para colar a tela do PageSpeed. Puxe os insights sozinho:

```
python3 medir.py <slug>          # celular (o que mais reprova)
python3 medir.py <slug> --both   # celular + desktop
```

O `medir.py` chama a API oficial do Google (mesma engine do site pra pagina JA
NO AR) e ja separa o que da pra consertar AQUI (imagem grande, coisa que trava a
abertura) do que NAO e do codigo (tags do Google Tag Manager / Facebook,
Cloudflare, dominio de terceiro estranho — isso se resolve no painel do Google).
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
Para sozinho quando a nota bate, quando nao ha mais imagem p/ encolher (o resto e
peso de terceiro, fora do codigo), ou no limite de rodadas. Nunca mexe em
cor/contraste sozinho (isso e design, nasce certo no Claude Design).

## Pagina que precisa de algo VIVO (contador, dado ao vivo, algo que muda sozinho)

Cuidado: o publicar tira UMA FOTO da pagina e joga fora o motor (React). O que vai
ao ar e estatico — leve e rapido, mas PARADO. Contador nao anda, barra nao atualiza,
nada reage no navegador do visitante; so muda quando a pagina e republicada.

Por isso, script proprio colado no HTML-fonte NAO funciona no ar (o estatizador
remove todo `<script>`). O publicar BARRA e pede confirmacao quando isso acontece
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

## O que e automatico (nao precisa conferir a cada pagina)

Imagens e fontes viram arquivos externos e WebP; a capa sai mais leve para o
LCP; a pagina e pre-montada estatica sem React; o pixel e adiado; entram
`lang=pt-BR` e `role=main`; hover dos botoes e animacoes de entrada; cache
longo com `.htaccess`; e o cache do Cloudflare e limpo inteiro ao publicar.
