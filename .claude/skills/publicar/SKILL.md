---
name: publicar
description: Publica paginas do repositorio cm-pages na hospedagem da Contem Magia e espelha no GitHub. Use SEMPRE que o usuario pedir para publicar, subir, colocar no ar, atualizar ou republicar uma pagina, disser "publica o coe", "sobe essa pagina", "poe no ar", "atualiza a pagina X", ou quando uma pagina nova exportada do Claude Design entrar no repositorio e precisar ir para a hospedagem. Cobre tambem a conferencia de peso e contraste antes de subir e a nova pagina a partir de uma exportacao do Claude Design.
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
   celular e no desktop e pode avisar duas coisas:
   - *imagem maior que o necessario* — ele imprime o `reduzir.json` pronto
   - *contraste abaixo de 4,5* — ele mostra a cor e o fundo que reprovaram
   Isso e aviso, nao erro: a publicacao continua. Trate como sinal de que a
   proxima exportacao do Claude Design deve nascer certa
   (ver `_padroes/checklist-design.md`), nao como tarefa de conserto recorrente.
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
