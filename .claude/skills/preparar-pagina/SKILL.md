---
name: preparar-pagina
description: Conduz nova exportação do Claude Design ou migração de página até um preview fiel, funcional e otimizado no cm-pages. Coordena otimizar e publicar conforme o pedido; não é o fluxo de manutenção de ajustes pequenos.
---

# Preparar página

Transformar uma página recebida em uma entrega fiel, funcional e rápida.
Leia `CLAUDE.md`. Preserve o original e confirme a slug/destino pelo pedido;
checkout padrão é `pay.contemmagia.com.br/c/<slug>`, salvo indicação diferente.
Não exija nova exportação do dono para problema técnico resolvível aqui.
Não acione esse fluxo para ícone, cor ou correção delimitada.

## Condução

1. **Decida o que a página precisa ANTES de construir.** Identifique o formato
   (HTML direto, WordPress ou bundler Claude Design), leia `<slug>/REGRAS.md` se
   existir e faça inventário de conteúdo, links de compra, UTM, FAQ, formulários
   e interações. No bundler, o React é removido depois do pré-render: só
   sobrevive o JavaScript de `estatico.py` — animação (`data-anim`, `data-hero`),
   contador/vagas (`data-cd`, `data-encerrado`, `data-fill`, `data-sempct`) e o
   repasse de UTM no checkout. Interação fora dessas alças exige código novo no
   `LIVE_JS`; o pipeline só avisa no stderr, depois do build. O bundler também
   exige Chrome: sem pré-render o build morre de propósito, para não publicar React.
   Migração WordPress: leia `docs/engenheiro-kit.md` antes de escrever o HTML e
   siga `docs/RECEITA-PAGINAS.md` como passo a passo.
2. **Configure antes do primeiro build.** Rastreamento é padrão do repo, não do
   original: um GTM só e `<slug>/rastreamento.json` (§ Rastreamento do kit).
   Ajuste de carregamento entra por `<slug>/desempenho.json`, nunca editando o
   HTML à mão. Ambos derrubam o build quando inválidos — configure agora, não
   depois de conferir.
3. **Construa uma vez:** `python3 preparar.py <slug>` (sai em `.build/<slug>`,
   que é o que `./publicar.sh <slug>` reaproveita). Preparar em outra pasta só
   com o compromisso de publicar com `--build <mesma pasta> <slug>`: misturar os
   dois reconstrói tudo, e no bundler o rebuild recaptura animação e cronômetro.
4. **Confira fidelidade e funcionamento** em celular e desktop: imagens e fundos,
   tipografia, overflow, respostas de FAQ, CTAs e compra sem transações.
   Interação nova se exercita no preview; nota alta não prova fidelidade.
   Corrija os defeitos e só então rode `preparar.py <slug> --conferir` uma vez,
   no build final — é o mesmo que vai ao ar. Código 2 é aviso de imagem pesada
   ou contraste (sugere `reduzir.json`/`cores.json`), não falha de preparação.
   Rastreamento tocado: `python3 scripts/testar-rastreamento.py`.
5. **Desempenho só quando é o assunto.** Com pedido de desempenho ou gargalo
   concreto, chame `otimizar` e consulte apenas a seção técnica do gargalo em
   [referência técnica](../otimizar/REFERENCIA-TECNICA.md). Sem isso, entregue o
   que `otimizar.py` + `desempenho.json` já aplicam; PageSpeed público exige a
   página no ar.
6. **Encerre no que foi pedido.** Pedido de preview termina no preview: entregue
   o caminho e o que ficou pendente. Se o pedido já inclui publicar, siga com
   `publicar` enviando o mesmo build validado, sem pedir aprovação de novo.

## Encerramento proporcional

Agrupe correções no preview e reaproveite as provas da mesma versão; não
republique nem remeça a cada microajuste. Meta de nota vem do pedido, não do
fluxo. Defina o próximo passo pelo que falta no aceite, não por uma sequência
fixa de ferramentas.
