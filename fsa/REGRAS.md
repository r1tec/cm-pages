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
  demais imagens lazy. Fontes Latin e Latin-ext são as fornecidas no arquivo;
  manter Latin-ext para Ọmọlúàbí e Àṣẹ. Preload apenas das quatro fontes Latin.
- O arquivo exportado referencia em JS versões `img/fsa-*.jpg`/`img/bg.jpg` que
  não foram incluídas: manter os recursos UUID realmente fornecidos. Não criar
  URLs fictícias nem deixar o script substituir as imagens válidas.
- Página precisa continuar responsiva após remover React. Não congelar tamanho
  de imagem/colunas calculado no desktop ou no celular durante o pré-render.
- Publicar pelo pipeline e validar mínimo90 no PageSpeed mobile e desktop,
  além de links, FAQ, imagens, contraste e ausência de erros JS.
