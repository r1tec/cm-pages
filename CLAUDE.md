# Motor de páginas — regras comuns (cm-pages e rp-pages)

Global do executor: Claude `~/.claude/CLAUDE.md`; Codex `~/.codex/AGENTS.override.md`.
`AGENTS.md` = este arquivo. Skills na fonte `.claude/skills/`; `.agents/skills/`
só aponta para elas, sem cópias concorrentes.

**Dados e regras do site deste projeto: `.claude/CLAUDE.md`** (domínio, marca,
checkout, rastreamento, hospedagem, o que se pode tocar na raiz, remoto Git e
documentos próprios). O Claude carrega os dois sozinho; Codex e outros executores
leiam `.claude/CLAUDE.md` inteiro antes de começar. Quando ele diverge deste
arquivo num ponto do site, vale ele.

## Arquivos comuns aos dois projetos

Este `CLAUDE.md` e `.claude/skills/` são os mesmos no cm-pages (Contém Magia) e no
rp-pages (Rogeria Pinheiro). A fonte única mora em
`/Users/raphaelmartins/orca/projects/cm-pages`; no rp-pages os dois são links para lá.

- Mudar regra comum ou skill, de qualquer um dos projetos, muda os dois. O commit
  vai no repositório cm-pages (`git -C /Users/raphaelmartins/orca/projects/cm-pages`),
  só com esses arquivos, e segue as regras de Git do cm-pages.
- Fato ou regra de um site só vai no `.claude/CLAUDE.md` daquele projeto, nunca
  aqui nem nas skills. Skill fala em "seção do site" e não cita domínio, marca,
  checkout ou documento de um projeto só.
- O código do motor (`preparar.py`, `estatico.py`, `publicar.sh` etc.) NÃO é
  comum: cada projeto tem a sua cópia.
- No rp-pages, se as skills sumirem ou este arquivo não abrir, o link quebrou
  (cm-pages movido ou renomeado): recrie o link, não copie os arquivos.

## Fontes

- Skills: `publicar` envia a versão escolhida; `otimizar` cuida de desempenho;
  `preparar-pagina` conduz páginas novas; `seo` cuida do SEO. Manutenção pequena
  não aciona o fluxo completo.
- Antes de editar páginas: `<slug>/REGRAS.md`, quando existir, e os padrões
  `_padroes/checklist-design.md` e `_padroes/prompt-claude-design.md`.
- Retomar trabalho: plano ou handoff correspondente em `docs/`. Documentos
  antigos não autorizam novas ações. Preserve texto aprovado, checkout,
  parâmetros de campanha, rastreamento e trabalho local alheio.

## Velocidade e travas contra refação

- Pedido claro executa direto; pare para validar só em publicação sem pedido,
  checkout/rastreamento com efeito real ou pedido ambíguo (regra global). Erro que
  impede o objetivo da missão (ex.: `robots.txt` quebrado barrando o Google) faz
  parte dela: corrija e siga, sem pedir licença. Termine a tarefa e pare: nada de
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
slug publica todas). Outros caminhos de envio (workflow, cPanel, FTP avulso) não
se usam nem se reativam.

- **Publicar ou afinar só com pedido** aplicável à tarefa ("publica", "sobe"). O
  pedido vale até o fim da tarefa e entre sessões: não repergunte. Editar ou
  diagnosticar sozinho não autoriza pôr no ar.
- O que um pedido de publicar pode tocar além da pasta da página (arquivos da raiz
  do domínio) está na seção do site. Antes de trocar um arquivo da raiz, guarde o
  anterior para reverter.
- Defeito apontado pelo dono numa página publicada na tarefa: corrige, valida e
  republica no mesmo destino ("Continuação após entrega" do global).
- Valide conforme a mudança e reutilize as provas da mesma versão. Ícone/cor/ajuste
  pequeno pede teste do componente; PageSpeed só por pedido de desempenho ou impacto
  concreto. Documentação não exige publicar ou reconstruir páginas.

Credenciais ficam no `.env`, fora do Git: não exibir nem versionar.

## Git

- Trabalho direto na `main`. Trabalho concluído termina com commit (e push, quando
  a seção do site autoriza), só dos arquivos da tarefa; mudança local alheia fica
  fora do commit. Commits pequenos em português, um assunto por commit.
- Nunca `--force`, rebase de história publicada ou `--no-verify`.

## Falar comigo

- Segue `~/.claude/rules/concisao.md`. Não leio código: linguagem simples, essência.
- Comece pelo resultado; com página publicada, dê a URL.
- Ação minha só se existir, sozinha na última linha, começando pelo verbo.
