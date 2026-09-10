# Formação Saberes Ancestrais

- Fonte aprovada: `Formacao Saberes Ancestrais - Pagina de Vendas v2.html`,
  fornecida pelo dono em 10/09/2026. Importação reproduzível por
  `scripts/preparar-fsa.py`; nunca altera o original.
- Rota solicitada: https://contemmagia.com.br/fsa/.
- Preservar copy, ofertas, garantia e nove perguntas/respostas da exportação.
  Checkout principal `https://pay.contemmagia.com.br/c/fsa`; oferta alternativa
  mantém `?offer=alt`. Propagar UTM sem substituir esse parâmetro existente.
- Sem chat: instalar apenas em novo pedido explícito. GTM segue rastreamento.py,
  primeira interação ou cinco segundos; não duplicar pixels diretos.
- FAQ nativo, imagem principal com proporção reservada e enquadramento por CSS,
  demais imagens lazy. Fontes são as fornecidas no arquivo: subconjuntos Latin
  incorporados e preload das três famílias críticas; Latin-ext continua externo
  para Ọmọlúàbí e Àṣẹ. `scripts/preparar-fontes-fsa.py` regenera os subconjuntos
  da exportação original (fonttools + brotli), antes de `preparar-fsa.py` quando
  mudar a copy. Preservar métricas, eixos e composição tipográfica padrão.
- O arquivo exportado referencia em JS versões `img/fsa-*.jpg`/`img/bg.jpg` que
  não foram incluídas: manter os recursos UUID realmente fornecidos. Não criar
  URLs fictícias nem deixar o script substituir as imagens válidas.
- Página precisa continuar responsiva após remover React. Não congelar tamanho
  de imagem/colunas calculado no desktop ou no celular durante o pré-render.
- Hero mobile sem spacer de fotografia antes do texto: preservar fonte/copy e
  apresentar o primeiro botão na primeira tela usual, com fundo legível. Desktop
  deve ter mistura contínua da foto, sem borda vertical em nenhuma largura.
- No bloco de reconhecimento, coluna de texto desktop usa 60% da largura antes
  do desconto do gap. Overlays decorativos não devem receber animação de entrada.
- Atalhos mobile precisam compensar o menu de duas linhas; conferir os quatro
  destinos e o título do FAQ ao clicar, inclusive ao ampliar o texto.
- Publicar pelo pipeline e validar mínimo90 no PageSpeed mobile e desktop,
  além de links, FAQ, imagens, contraste e ausência de erros JS.
