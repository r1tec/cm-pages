# Checklist de design — antes de exportar do Claude Design

Três regras. Se as três nascem certas aqui, as correções pós-exportação
(`reduzir.json`, `cores.json`) deixam de existir.

## 1. Contraste do texto

Todo texto precisa de contraste mínimo sobre o fundo em que ele está:

- texto normal: **4,5:1**
- texto grande (24px+, ou 18,5px+ em negrito): **3:1**

O laranja da marca `rgb(255, 67, 0)` dá **3,47:1** no branco — reprova em
texto normal. Use as variantes já validadas em `tokens.json`:

- laranja para **fundo** de botão (com texto branco em cima): `rgb(200, 50, 0)`
- laranja para **texto** sobre fundo escuro: `rgb(255, 110, 60)`
- o laranja original só em elemento decorativo sem texto (barra, ícone, borda)

## 2. Pesos de fonte: no máximo 4

O Design exporta todos os pesos e todos os idiomas da família. Cada peso extra
é um arquivo a mais para o visitante baixar. Escolha 3 ou 4 e use só eles
(ex.: 400 / 600 / 700). Isso é peso economizado de graça, sem tocar em nada
depois.

## 3. Tamanho das imagens

Exporte cada imagem no **dobro** do maior tamanho em que ela aparece na tela
(retina), não maior. Uma foto de 4000px exibida num card de 200px faz o
visitante baixar 20x mais bytes do que vai ver.

Se não souber o tamanho final, publique uma vez e rode `./publicar.sh` — a
conferência automática mede a página no celular e no desktop e diz, imagem por
imagem, o tamanho certo.

## Fora do checklist (é automático, não se preocupe)

O `publicar.sh` já resolve sozinho, toda vez: WebP, cache, pré-montagem
estática sem React, pixel adiado, `lang=pt-BR`, `role=main`, hover dos botões,
animações de entrada e limpeza do cache do Cloudflare.
