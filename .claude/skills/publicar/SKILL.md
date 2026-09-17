---
name: publicar
description: Publica páginas preparadas do cm-pages, reutiliza builds, limpa cache e confirma a entrega. Use para publicar ou republicar uma versão escolhida. Não inicia otimização nem PageSpeed por padrão.
---

# Publicar

Entregar a versão escolhida no destino autorizado, com confirmação breve.
Leia `CLAUDE.md`. Pedido de publicar não é pedido de otimizar; edição ou preview
não autorizam publicação. Autorização vigente para a mesma tarefa não precisa
ser renovada a cada etapa. Respeite slugs, destino e o limite mais recente.

## Caminho curto

1. Identifique a página e a versão solicitadas. Preserve mudanças locais alheias.
2. Se o preview já foi preparado e validado, publique esse build:
   `./publicar.sh --build /tmp/preview-mce mce`.
   Sem preview escolhido: `./publicar.sh mce` reutiliza `.build/mce` se atual;
   caso contrário, prepara uma vez. Não use o modo sem slugs para pedido pontual.
3. Leia o resultado do envio/cache. Confirme HTTP e a versão pública entregue
   (comparação do HTML/asset modificado com o build). Se o funcionamento já foi
   validado nessa mesma versão, não repita o roteiro completo de navegador.
4. Registre e envie somente o trabalho da tarefa ao GitHub; informe a URL e
   eventual falha real. Um ajuste pequeno não exige relatório novo extenso.

`publicar.sh` é a única entrada de envio. Não usar FTP paralelo, reativar workflow
ou `.cpanel.yml`. O comando preserva os destinos/espelhamento configurados e limpa
cache por prefixo, inclusive campanhas. `.env` contém credenciais; não exibir.

O manifesto do build prova correspondência com a fonte e integridade dos arquivos,
não aprovação visual. `--build` recusa um build alterado ou desatualizado, sem
reconstruí-lo silenciosamente. Refaça o preview se a versão escolhida mudou.
Builds antigos feitos diretamente por `otimizar.py` precisam passar uma vez por
`preparar.py` para ganhar manifesto; não crie hashes para aprovar uma saída incerta.

## Verificação proporcional

| Mudança | Verificação pertinente antes de enviar |
| --- | --- |
| Ícone, cor, selo, texto curto ou animação pequena | Componente e estados afetados; sem PageSpeed por padrão |
| Layout/responsividade | Regiões e larguras afetadas |
| Checkout, UTM ou rastreamento | Fluxos/eventos afetados, sem transações ou mensagens reais |
| Fontes críticas, imagem principal, dependências ou agendamento de scripts | Avaliar impacto visual/desempenho; medir se houver motivo concreto |
| Página nova ou reformulação ampla | Usar `preparar-pagina` para preparar e validar |

Não transforme uma correção em auditoria geral. Um bug do ícone ao abrir o chat
exige testar aberto/fechado, não recomprimir imagens nem medir toda a página.
Preserve as provas válidas do preview. Repetir só por mudança, falha ou dúvida
concreta. Pedido explícito de apenas enviar a versão validada usa o caminho curto.

## Quando chamar outra skill

- Pedido de desempenho ou regressão concreta: `otimizar`.
- Nova exportação Claude Design/WordPress: `preparar-pagina`.
- Ajuste simples: resolva na própria sessão e publique quando autorizado.

Não leia referências de otimização para uma publicação comum. Comandos de
preparação/reuso estão em `README.md`; configuração atual dos destinos em
`docs/PUBLICACAO-EDU.md`, somente se o destino/espelho estiver envolvido.

## GitHub após publicação

Commit + push na `main` de `origin` (`https://github.com/r1tec/cm-pages.git`)
seguem a seção Git do `CLAUDE.md`, sem pedir permissão (autorização do dono em
11/09/2026): só os arquivos da tarefa, sem segredos nem mudanças alheias.
Bloqueio automático da ferramenta não é falha: o dono roda por `!`.

Pedido de publicar vale até o fim da tarefa e entre sessões. Correção apontada
pelo dono na página publicada republica no mesmo destino sem novo pedido.
