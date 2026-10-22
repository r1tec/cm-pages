# Site deste projeto: Contém Magia (cm-pages)

Regras comuns do motor: `CLAUDE.md` na raiz (vale para cm-pages e rp-pages).
Aqui ficam só os fatos e as regras deste site.

Páginas de venda da Escola Contém Magia. Cada pasta com `index.html` é uma rota
em `https://contemmagia.com.br/<slug>`. Há exportações autocontidas do Claude
Design e páginas reescritas em HTML leve a partir do WordPress.

## Fontes deste site

- Operação: `README.md`.
- Recriar WordPress: `docs/RECEITA-PAGINAS.md` e `docs/engenheiro-kit.md`
  (leia o kit antes de escrever o HTML; a receita é o passo a passo).
- Desempenho ligado a domínio/GTM: `docs/PERFORMANCE-MIGRACAO.md` (também a
  autorização do GTM adiado e a referência histórica detalhada).
- Chat nas páginas: `docs/CHAT-PAGINAS.md` (instalar ou mudar carregamento;
  mudar só o desenho do ícone usa verificação do componente, sem PageSpeed).
- Destino espelhado (Edu): `docs/PUBLICACAO-EDU.md`, só se o espelho estiver
  envolvido. `publicar.sh` já preserva o espelhamento configurado.
- SEO: método, evidências e limites em `docs/PLANO-SEO.md` (leia "Como escolher
  as palavras" e "Builds"); fontes em `docs/seo/`. Semente de marca:
  `"<produto> edu parmeggiani"`; use a grafia que as pessoas buscam (ex.: "pomba
  gira" além de "Pombogira"; curiosidade: "reza contra mau olhado").
- Rastreamento de página nova: § Rastreamento do `docs/engenheiro-kit.md`.
- Fontes incorporadas da FSA: o gerador reproduzível é `scripts/preparar-fontes-fsa.py`.

## Checkout e rastreamento

- Checkout padrão: `pay.contemmagia.com.br/c/<slug>`, salvo indicação diferente.
- GTM `GTM-P629X98`, fonte única em `rastreamento.py`. Pixels observados na
  configuração vigente: `197461362094441` e `884049927923756`; verificar a
  configuração atual sem alterar IDs por inferência.
- Exceção autorizada em 12/09/2026: piloto DRB com Meta antecipada, opt-in em
  `drb/rastreamento.json`. Seguir `docs/PLANO-DRB-PIXEL-ANTECIPADO.md` para
  publicar/reverter. O adaptador evita a primeira repetição das chamadas Meta do
  container v28; revalidar se as tags mudarem; não copiar o piloto para outras
  páginas sem escopo aplicável.
- Rastreamento tocado: `python3 scripts/testar-rastreamento.py`.
- Página viva do evento ECM: `LIVE_JS` no `estatico.py` (alças `data-cd`,
  `data-encerrado`, `data-fill`, `data-sempct`); interação fora dessas alças
  exige código novo nele.

## Publicação e raiz do domínio

- O destino de um pedido de publicar é o domínio inteiro, não só a pasta da página:
  arquivos da raiz que a missão precisa (`robots.txt`, sitemap, home, 404, `.htaccess`)
  entram sem nova consulta. A raiz não tem WordPress ativo, só restos dele: não
  trate como site no ar.
- GitHub é espelho; workflow FTP e `.cpanel.yml` estão desativados de propósito.
- Home, página Sobre e sitemap: `raiz.py`, que lê `config/raiz/paginas.json`
  (`nome` e `resumo`; variações de teste e eventos encerrados ficam fora). Página
  nova entra no `paginas.json` e, ao publicar, rode `python3 raiz.py --publicar`
  (também avisa Bing e outros buscadores pelo IndexNow).
- Search Console: propriedade de domínio `contemmagia.com.br`, conta
  operacoes@raiz1.com.br; sitemap enviado em 19/10/2026. Depois de publicar
  página nova, peça indexação da URL.
- Página de venda sem link que não seja o checkout (decisão do dono, 19/10/2026:
  zero distração). A ligação entre as páginas fica na home e em /sobre/.
- Caso `coe` (19/10/2026): a página no ar veio de versão antiga do pipeline e o
  SEO foi aplicado sobre o HTML publicado. Por isso, nunca republicar página cujo
  build diverge do que está no ar sem conferir o corpo contra a versão publicada.

## Migração do WordPress

Página do `lp.eduparmeggiani.com` publicada em `contemmagia.com.br`: confira a
página em `docs/LISTA-SITES-WORDPRESS.md` antes e, na mesma tarefa, marque a
linha como "Sim" com a URL, total e data corrigidos, e inclua o arquivo no commit.
Slug novo no WordPress que ainda não esteja na tabela entra como "Não".

## Git

- Remoto `origin` = `https://github.com/r1tec/cm-pages.git`. Commit + push na
  `main` sem pedir permissão (autorização do dono em 11/09/2026): só os arquivos
  da tarefa, sem segredos nem mudanças alheias. Bloqueio automático da ferramenta
  não é falha: o dono roda por `!`.
- Sessão que nasceu numa worktree (trabalho em segundo plano): ao terminar, junte a
  branch na `main` você mesmo (`git merge`, sem rebase) e faça push. Esta linha é a
  autorização do dono para push na `main` neste repositório; ele não roda git.
