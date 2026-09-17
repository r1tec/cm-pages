---
name: otimizar
description: Diagnostica e melhora desempenho de páginas cm-pages, incluindo PageSpeed, fontes, imagens e scripts. Use quando há pedido de desempenho ou regressão concreta. Não se aplica automaticamente a toda edição ou publicação.
---

# Otimizar

Melhorar o carregamento real dentro do escopo pedido. Leia `CLAUDE.md` e preserve
conteúdo, identidade visual, compras, campanhas, rastreamento e atendimento.
Não publica sem autorização aplicável; pedido só de medir termina no diagnóstico.

## Escolher a profundidade

- Pergunta ou medição pontual: obter o dado e interpretar o que ele demonstra.
- Gargalo delimitado: investigar a causa, ajustar e verificar o efeito afetado.
- Otimização completa/máxima performance: avaliar todos os audits recebidos nos
  dois dispositivos, priorizar por impacto e resolver os ganhos demonstráveis.
  Não descartar automaticamente itens informativos ou economias pequenas; também
  não criar trabalho para audits aprovados ou estimativas sem ganho comprovado.

Use evidência recente da mesma versão como referência quando disponível. Nova
coleta é necessária para mudança relevante ou lacuna, não para repetir uma prova
válida. Desempenho visual (FCP/LCP/CLS) e trabalho de processamento (TBT) importam
mais do que perseguir um único número.

## Fluxo

1. Identifique o gargalo com rede/DOM/CPU e PageSpeed quando pertinente:
   `python3 medir.py mce --both --tentativas 1 --output /tmp/psi-mce.json`.
2. Faça alterações técnicas com hipótese verificável, preservando a função.
3. Prepare com `python3 preparar.py mce --saida /tmp/preview-mce` e verifique
   o impacto visual/funcional pertinente. `--conferir` adiciona auditoria de
   imagens/contraste quando útil; não é parte obrigatória de todo build.
4. Com publicação já autorizada, use `publicar` para enviar o build validado e
   compare o resultado público relevante. Sem autorização, entregue o preview.
5. Termine quando o objetivo for atingido e as oportunidades restantes não
   tiverem ganho demonstrável, exigirem mudança de escopo ou estiverem bloqueadas.

Em pedidos amplos, use 90+ móvel/desktop como referência inicial quando não houver
outra meta. “Máxima performance” pede avaliar e testar os ganhos úteis, não buscar
100 indefinidamente, remover funcionalidades ou repetir coletas até aparecer verde.
Se a meta não for alcançável no escopo, explique o gargalo e a decisão necessária.

## Medição e indisponibilidade

`medir.py` usa PSI_API_KEY local; não exibir a chave. Erro não é nota. 500/502/503/
504 ou timeout: registre a falha, avance com trabalho independente e retome quando
isso ajudar a decisão; não mantenha o fluxo preso em espera para ajuste pequeno.
Em lote, tente a próxima página e revisite pendências elegíveis; respeite
`Retry-After`. 429 exige avaliar cota; 401/403 exige conferir acesso, sem retries
cegos. Uma medição indisponível não impede commit/push de trabalho publicado e
funcionalmente validado; informe a limitação e não declare desempenho comprovado.

Não selecionar só a melhor amostra nem atribuir variação ao último ajuste sem
evidência. Core Web Vitals histórico de 28 dias não é a nota Lighthouse atual.

## Referências sob demanda

- [REFERENCIA-TECNICA.md](REFERENCIA-TECNICA.md): consulte a seção pertinente a
  fonte/primeira pintura, imagens, CSS, renderização estática, rastreamento ou
  análise dos audits. Não carregar tudo para um ajuste pontual.
- `docs/PERFORMANCE-MIGRACAO.md`: investigação relacionada a domínio/GTM.
- `docs/CHAT-PAGINAS.md`: instalar chat ou mudar seu carregamento; mudança apenas
  no desenho do ícone usa verificação do componente, sem PageSpeed automático.
- `afinar.sh`: auxiliar legado restrito a imagens, publica e mede em rodadas.
  Só usar com autorização para essas publicações; não substitui o diagnóstico.

GTM permanece por interação ou até 5 s; piloto Meta antecipado só nas páginas
com opt-in aprovado. Chat apenas se solicitado, com atendimento e prazo daquela
página. Não copiar esses ajustes entre campanhas por conveniência.
