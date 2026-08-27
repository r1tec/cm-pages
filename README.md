# Contém Magia Pages

**Para publicar, dentro desta pasta:** `./publicar.sh` (ou `/publicar` no Claude Code)

Páginas de venda estáticas da Escola Contém Magia. Cada pasta da raiz é uma rota:

```
coe/index.html   ->  https://contemmagia.com.br/coe
```

Cada `index.html` é a exportação do Claude Design: autocontido, sem framework,
sem CDN, sem build. É normal ele ter vários MB — o `publicar.sh` enxuga na hora
de subir, sem alterar o arquivo fonte.

## O processo, em quatro etapas

1. **Copy travada** — texto aprovado antes do design começar.
2. **Design no Claude Design** — layout, cor, imagem, fonte. As três regras de
   `_padroes/checklist-design.md` valem aqui: contraste 4,5, no máximo 4 pesos
   de fonte, imagem no dobro do tamanho exibido.
3. **`./publicar.sh <slug>`** — otimiza, confere e sobe.
4. **Commit e push** — o GitHub é o espelho, a hospedagem é o resultado.

## Publicar

```
./publicar.sh          # todas as páginas
./publicar.sh coe      # só a slug coe
```

Antes de enviar, o script mede a página no celular e no desktop e avisa se
alguma imagem está maior que o necessário ou se algum texto está com contraste
abaixo de 4,5 — e imprime o `reduzir.json` / a troca de cor prontos. É aviso,
não erro: a publicação continua. Se um aviso se repete, o lugar de corrigir é o
Claude Design, não o remendo local.

**Este é o único caminho de publicação.** O workflow do GitHub Actions e o
`.cpanel.yml` foram desativados: subiam o arquivo cru, sem otimizar e sem
limpar o cache, por cima do resultado do `publicar.sh`.

## Máquina nova / outra pessoa da equipe

```
git clone https://github.com/r1tec/cm-pages.git
cd cm-pages
cp .env.example .env      # preencher FTP_SENHA e CF_API_TOKEN
./publicar.sh
```

O comando `/publicar` vem junto com o clone — mora em `.claude/skills/publicar`.
Requisitos na máquina: `python3`, `lftp` (instalado automaticamente via
Homebrew) e Google Chrome (usado para pré-montar a página e para medir peso e
contraste).

## Estrutura

```
_padroes/              regras de design compartilhadas por todas as páginas
.claude/skills/        o comando /publicar, versionado junto com o repo
<slug>/index.html      a página, exportada do Claude Design
<slug>/REGRAS.md       regras de conteúdo daquela página
<slug>/reduzir.json    remendo local: encolher imagens (evite; corrija no Design)
<slug>/cores.json      remendo local: trocar cores por contraste (idem)
otimizar.py            peso, WebP, cache
estatico.py            pré-monta a página sem React
verificar.py           confere imagem e contraste, só avisa
publicar.sh            o publicador
```
