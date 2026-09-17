# cm-pages — canônico do projeto

Global do executor: Claude `~/.claude/CLAUDE.md`; Codex `~/.codex/AGENTS.override.md`.
`AGENTS.md` = este arquivo. Skills na fonte `.claude/skills/`; `.agents/skills/`
só aponta para elas, sem cópias concorrentes.

Páginas de venda da Escola Contém Magia. Cada pasta com `index.html` é uma rota
em `https://contemmagia.com.br/<slug>`. Há exportações autocontidas do Claude
Design e páginas reescritas em HTML leve a partir do WordPress.

## Fontes

- Operação: `README.md`. Skills: `publicar` envia a versão escolhida; `otimizar`
  cuida de desempenho; `preparar-pagina` conduz páginas novas. Manutenção pequena
  não aciona o fluxo completo.
- Antes de editar páginas: `<slug>/REGRAS.md`, quando existir, e os padrões
  `_padroes/checklist-design.md` e `_padroes/prompt-claude-design.md`.
- Recriar WordPress: `docs/RECEITA-PAGINAS.md` e `docs/engenheiro-kit.md`.
- Retomar trabalho: plano ou handoff correspondente em `docs/`. Documentos
  antigos não autorizam novas ações. Preserve texto aprovado, checkout,
  parâmetros de campanha, rastreamento e trabalho local alheio.

## Velocidade e travas contra refação

- Pedido claro executa direto; pare para validar só em publicação, checkout/rastreamento
  com efeito real ou pedido ambíguo (regra global). Termine a tarefa e pare: nada de
  melhoria não pedida; se vê algo melhor, 1 frase e siga.
- Lista longa, cortada ou com imagem: devolva o entendimento (1 linha/item) antes de executar.
- Bug: reproduza antes de corrigir (preview, navegador ou página pública).
- **"Pronto" só com o resultado real visto na mesma mensagem.** Interação nova
  (FAQ, chat, contador, botão de compra sem comprar) se exercita no preview;
  screenshot prova pixel, não comportamento. Olhe o print caçando defeito
  (corte, sobreposição, fundo, overflow), não só "renderizou".
- Opinião sobre a página ou o pipeline vem com evidência (arquivo, trecho, medição)
  na mesma mensagem; antes de criar mecanismo, procure o que já existe (`estatico.py`,
  `rastreamento.py`, `preparar.py`).

## Pipeline e publicação

`preparar.py` produz o build com manifesto e cache de imagens; `--conferir`
adiciona a conferência visual quando pertinente. `publicar.sh` reutiliza o build
atual ou prepara uma vez se necessário; `--build <pasta> <slug>` exige exatamente
um build íntegro e atual, sem reconstruí-lo. O envio usa uma cópia conferida,
FTP e limpeza de cache por prefixo. Não roda PageSpeed ou auditoria visual por
padrão. `estatico.py` remove o motor React da exportação pré-renderizada;
interações necessárias dependem do JavaScript leve previsto nele.
`medir.py` consulta PageSpeed; `afinar.sh` publica e mede em rodadas limitadas.

Único caminho de publicação: `./publicar.sh <slug ...>` (slugs explícitas; sem
slug publica todas). GitHub é espelho; workflow FTP e `.cpanel.yml` estão
desativados de propósito. Não reativá-los.

- **Publicar ou afinar só com pedido** aplicável à tarefa ("publica", "sobe"). O
  pedido vale até o fim da tarefa e entre sessões: não repergunte. Editar ou
  diagnosticar sozinho não autoriza pôr no ar.
- Defeito apontado pelo dono numa página publicada na tarefa: corrige, valida e
  republica no mesmo destino ("Continuação após entrega" do global).
- Valide conforme a mudança e reutilize as provas da mesma versão. Ícone/cor/ajuste
  pequeno pede teste do componente; PageSpeed só por pedido de desempenho ou impacto
  concreto. Documentação não exige publicar ou reconstruir páginas.

Credenciais ficam no `.env`, fora do Git: não exibir nem versionar.

## Git

- Trabalho direto na `main` (o GitHub não publica nada). Trabalho concluído termina
  com commit + push juntos, só dos arquivos da tarefa; mudança local alheia fica
  fora do commit. Commits pequenos em português, um assunto por commit.
- Nunca `--force`, rebase de história publicada ou `--no-verify`.

## Falar comigo

- Segue `~/.claude/rules/concisao.md`. Não leio código: linguagem simples, essência.
- Comece pelo resultado; com página publicada, dê a URL.
- Ação minha só se existir, sozinha na última linha, começando pelo verbo.
