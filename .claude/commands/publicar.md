---
description: Publica as páginas no ar (FTP) e sobe o código pro GitHub
---

Publica as páginas da pasta `cm-pages` na hospedagem e sincroniza o GitHub.

Argumento opcional: uma ou mais slugs (nomes de pasta). Sem argumento, publica todas.

Passos:

1. Rode o script de publicação:
   - Sem slug informado em `$ARGUMENTS`: `./publicar.sh`
   - Com slug(s): `./publicar.sh $ARGUMENTS`
2. Se houver mudanças no git, faça commit e `git push` para manter o GitHub espelhado.
3. Reporte ao Eduardo, em linguagem simples: quais páginas foram pro ar e os links `https://contemmagia.com.br/<slug>`.

Nunca peça a senha do FTP: ela já está no arquivo `.env`.
