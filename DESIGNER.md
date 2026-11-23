# Regras do designer (cm-pages)

Você cria e altera páginas de venda da Contém Magia. Nada que você faz vai ao
ar sozinho: você abre um pedido de revisão (PR) no GitHub, o Raphael confere a
prévia e aprova, e só ele publica.

Se você é um agente (Claude) na máquina do designer: este arquivo vence o
`CLAUDE.md` e o `.claude/CLAUDE.md` em tudo o que eles mandarem sobre main,
push, publicação e `.env`.

## O que nunca fazer

- **Nunca trabalhar na `main`** nem enviar (push) para ela. Todo trabalho fica
  numa branch `design/<slug>-<assunto>` (ex.: `design/drb-nova-capa`).
- **Nunca publicar**: não rode `./publicar.sh`, `afinar.sh`, `raiz.py --publicar`,
  FTP, cPanel nem nada que envie arquivos para o site.
- **Nunca criar, pedir nem copiar o `.env`** (senhas do site). Sua máquina não tem
  `.env`, e é assim que deve ficar.
- **Só mexer na pasta da página** (`<slug>/`). Em página nova, também pode
  acrescentar a página em `config/raiz/paginas.json` (só a entrada dela).
  Motor (`*.py`, `*.sh`, `scripts/`, `config/` no resto), `docs/`, `.claude/`,
  `.github/` e os arquivos da raiz ficam como estão.
- **Não mexer em `reduzir.json` nem `cores.json`** dentro da pasta: são ajustes
  de desempenho e contraste que o Raphael controla.
- **Texto, preço e link de compra exatamente como recebidos.** Não reescreva,
  não arredonde, não troque link. Faltou ou parece errado: pergunte no PR.
- Não crie links simbólicos e não commite com o nome ou e-mail de outra pessoa:
  use sempre o seu (ver "Preparar a máquina").

`rastreamento.json`, `seo.json` e `desempenho.json` da pasta podem ser
alterados quando o pedido exigir, mas aparecem destacados na revisão: diga no
PR por que mudou.

## Preparar a máquina (uma vez)

Precisa de um Mac com git, gh (GitHub), Python 3 com Pillow e Google Chrome.

```sh
# Homebrew (se ainda não tiver): https://brew.sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install git gh python pillow webp
brew install --cask google-chrome      # pule se o Chrome já estiver instalado

# Confere
git --version && gh --version && python3 -c "import PIL; print('Pillow', PIL.__version__)"
ls "/Applications/Google Chrome.app" >/dev/null && echo "Chrome ok"

# Sua identidade nos commits (seu nome e seu e-mail, nunca os do Raphael)
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"

# Entrar no GitHub com a SUA conta (convidada como colaboradora do repositório)
gh auth login
gh api user --jq .login                # tem que mostrar o seu login, não r1tec

# Baixar o projeto
git clone https://github.com/r1tec/cm-pages.git
cd cm-pages
```

## Começar um trabalho

```sh
git switch main
git pull --ff-only
git switch -c design/<slug>-<assunto>
```

Página que já existe: edite só a pasta dela. Página nova: crie a pasta
`<slug>/` com `index.html` (siga `docs/RECEITA-PAGINAS.md` e
`_padroes/checklist-design.md`) e acrescente a entrada em
`config/raiz/paginas.json` (grupo certo, `slug`, `nome` e `resumo`).

## Gerar a prévia

```sh
python3 preparar.py <slug> --saida /tmp/previa-<slug>
open /tmp/previa-<slug>/index.html
```

Confira no navegador, no celular e no computador (largura estreita e larga):
texto, preço, botão de compra, imagens. A prévia não usa senha nenhuma e não
publica nada.

## Abrir o PR

```sh
git add <slug>/                      # e config/raiz/paginas.json, se página nova
git commit -m "<slug>: o que mudou, em uma frase"
git push -u origin design/<slug>-<assunto>
gh pr create --base main --title "<slug>: o que mudou" \
  --body "O que foi pedido, o que mudou e o que conferir (preço, link, seções)."
```

Antes do push, confira que só a pasta certa mudou: `git status` e
`git diff --stat main`. Se aparecer outro arquivo, desfaça
(`git restore --source main -- <arquivo>`).

## Quando o Raphael pedir ajuste

O pedido chega como comentário no PR (`gh pr view --comments`). Ajuste na mesma
branch e envie de novo:

```sh
git switch design/<slug>-<assunto>
# faça o ajuste e gere a prévia de novo
git add <slug>/
git commit -m "<slug>: ajuste pedido na revisão"
git push
```

O PR se atualiza sozinho e volta para revisão. Cada envio novo pede uma
aprovação nova. Se o GitHub avisar conflito com a main, traga a main para a sua
branch (`git pull origin main`), mantenha as mudanças que a main fez e as suas
(nunca apague o que veio da main) e envie de novo.

## Depois da aprovação

O Raphael incorpora o PR e publica. Você não faz nada: para o próximo trabalho,
volte ao "Começar um trabalho".
