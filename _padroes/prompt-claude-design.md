# Prompt para começar uma página no Claude Design

Copie o bloco abaixo, preencha os `[colchetes]` e cole no Claude Design.
As restrições da segunda metade não mudam de página para página: são elas que
fazem a página nascer sem os remendos (`reduzir.json`, `cores.json`) e sem
retrabalho no `publicar.sh`.

---

## O bloco (copiar daqui)

```
Crie uma página de vendas de uma coluna, para celular primeiro, com a copy
abaixo. A copy está fechada: use o texto exatamente como está, sem reescrever,
sem cortar e sem acrescentar frase nenhuma. Seu trabalho é o visual.

PRODUTO: [nome] — [o que é, em uma linha]
PÚBLICO: [quem lê isso, em uma linha]
CLIMA: [ex.: ancestral e acolhedor, terroso, sem misticismo cafona]
SLUG: [ex.: coe]

COPY, dobra a dobra:
[cole aqui a copy inteira, marcando cada dobra
 DOBRA 1 - ...
 DOBRA 2 - ...]

BOTÃO DE COMPRA: texto sempre "[TEXTO EXATO]", link [URL]
Ele aparece [em quais dobras].

--- RESTRIÇÕES TÉCNICAS (não são preferência, a página é medida por elas) ---

CORES
- Todo texto precisa de contraste mínimo sobre o fundo em que está:
  4,5:1 no texto normal, 3:1 em texto grande (24px+, ou 18,5px+ em negrito).
- O laranja da marca rgb(255, 67, 0) dá 3,47:1 no branco e REPROVA em texto.
  Use assim:
    rgb(200, 50, 0)    fundo de botão e bloco, com texto branco em cima
    rgb(255, 110, 60)  texto laranja sobre fundo escuro
    rgb(255, 67, 0)    só em elemento decorativo sem texto (barra, ícone, borda)
- Qualquer cor nova que você propuser precisa passar nesses mínimos.

TIPOGRAFIA
- No máximo 4 pesos de fonte na página inteira. Sugestão: 400, 600, 700.
- Uma família só, mais uma de apoio se houver motivo real.

IMAGENS
- Cada imagem exportada no DOBRO do maior tamanho em que aparece na tela,
  nunca maior. Um selo exibido a 70px sai com 140px, não com 1000px.
- Considere o maior entre celular e desktop antes de decidir o tamanho.

O QUE NÃO FAZER
- Nada de animação, parallax, contador, carrossel automático ou efeito de
  rolagem. A publicação já adiciona hover nos botões e entrada suave, e
  qualquer motor de animação seu vira peso morto que é removido depois.
- Nada de vídeo de fundo, iframe, fonte de CDN externa ou biblioteca de ícone.
- Sem emoji e sem travessão no texto.

ESTRUTURA
- Uma coluna, blocos empilhados, respiro generoso entre dobras.
- A primeira dobra precisa fazer sentido sozinha, sem rolagem: título, uma
  linha de apoio e o botão.
- [regra específica desta página, ex.: nenhum preço antes da dobra da oferta]
```

---

## Depois que o Design entregar

1. Salve a exportação como `<slug>/index.html`.
2. Escreva as regras de conteúdo da página em `<slug>/REGRAS.md`.
3. Rode `./publicar.sh <slug>` e **leia a conferência**.
4. Se ela reclamar de imagem ou contraste, volte ao Claude Design com o aviso
   colado e reexporte. Só use `reduzir.json` / `cores.json` quando reexportar
   não for viável.

Um aviso que se repete em páginas diferentes não é problema da página: é sinal
de que falta uma linha neste prompt. Acrescente aqui.
