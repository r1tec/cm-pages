---
name: preparar-pagina
description: Conduz nova exportação do Claude Design ou migração de página até um preview fiel, funcional e otimizado no cm-pages. Coordena otimizar e publicar conforme o pedido; não é o fluxo de manutenção de ajustes pequenos.
---

# Preparar página

Transformar uma página recebida em uma entrega fiel, funcional e rápida.
Leia `CLAUDE.md`. Preserve o original e confirme a slug/destino pelo pedido.
Não exija nova exportação do dono para problemas técnicos que possam ser
resolvidos aqui. Não acione esse fluxo para ícone, cor ou correção delimitada.

## Condução

1. Identifique o formato: HTML direto, WordPress ou bundler Claude Design.
   Leia `<slug>/REGRAS.md` se existir e os padrões de design aplicáveis. Faça
   inventário do conteúdo, links de compra, UTM, FAQ, formulários e interações.
2. Prepare um build: `python3 preparar.py <slug> --saida /tmp/preview-<slug>`.
   O pipeline preserva os originais. No bundler, React é removido depois do
   pré-render; comportamentos necessários precisam sobreviver em JavaScript leve.
3. Confira fidelidade e funcionamento em celular/desktop. Verifique imagens e
   fundos, tipografia, overflow, respostas de FAQ, CTAs e compra sem transações.
   Use `--conferir` para a análise de imagens/contraste. Corrija defeitos antes
   de considerar o preview pronto; notas altas não provam fidelidade.
4. Use `otimizar` para a avaliação ampla de desempenho. Aplique melhorias com
   ganho comprovado, preservando aparência e funções. Consulte apenas as seções
   técnicas necessárias a esse formato/gargalo.
5. Entregue o preview no Orca quando solicitado. Se o pedido já incluir publicar,
   continue com `publicar` e envie o mesmo build validado; não peça aprovação
   novamente por uma etapa técnica. Pedido de preview encerra no preview.

Fontes técnicas de conversão: [referência técnica](../otimizar/REFERENCIA-TECNICA.md),
especialmente preparação de build e revisão visual. Para migração WordPress,
consulte também `docs/RECEITA-PAGINAS.md` e `docs/engenheiro-kit.md`.

## Encerramento proporcional

Meta de desempenho e nível de acabamento vêm do pedido. Em preparação completa,
buscar 90+ nos dois dispositivos como referência inicial e analisar o que ainda
traz ganho real. Não prometer 100 constante nem perseguir nota sem benefício.
PageSpeed público requer a página no ar; sem autorização de publicação, teste
localmente e distinga Lighthouse local de medição pública.

Agrupe correções no preview e reaproveite as verificações da mesma versão.
Não publicar após cada microajuste para medir novamente tudo. Defina próximos
passos pelo que falta no aceite, não por uma sequência fixa de ferramentas.
Agentes paralelos não são obrigatórios; só delegar quando houver ganho concreto
e autorização/instrução aplicável. Relatório detalhado é útil para uma página
nova complexa, não obrigatório para toda continuação pequena.
