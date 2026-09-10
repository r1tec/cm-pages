# FSA — publicação de 10/09/2026

Fonte: `~/Downloads/Formacao Saberes Ancestrais - Pagina de Vendas v2.html`,
3.531.984 bytes. Original preservado. Rota antes da instalação: HTTP404.
Destino autorizado: https://contemmagia.com.br/fsa/.

## Preparação e resultado

- Skill publicar revisada e novo PUBLICACAO-DESEMPENHO.md consolidando aceite90,
  diagnóstico por métrica, cache de campanhas, testes, fontes e chat só por pedido.
  Padrões de exportação/checklist alinhados; aprendizados do FSA acrescentados.
- `scripts/preparar-fsa.py` importa a fonte e mantém o build reproduzível. A
  exportação adaptada fica em fsa/index.html, com ajustes de contraste em cores.json.
- Bundler e React removidos do HTML servido. Vinte seções, nove imagens e nove
  perguntas/respostas preservadas. FAQ virou details/summary acessível, sem React.
- O script original trocava imagens embutidas por caminhos img/*.jpg inexistentes.
  Usados os arquivos realmente incluídos, com enquadramento responsivo. Grade e
  imagens não dependem do tamanho de viewport do pré-render. Atalhos cabem no celular.
- Mantidas fontes Latin e Latin-ext, inclusive para Ọmọlúàbí e Àṣẹ. Apenas quatro
  fontes Latin em preload; extensões sob demanda via unicode-range. Sem fontes de
  CDN. Imagem principal com preload e proporção reservada; demais imagens lazy.
- Cores de destaque clareadas sobre fundo escuro; tom escuro preservado no cartão
  claro. Conferência final do publisher: imagens no tamanho certo e contraste>=4,5.
- Title, descrição, canonical, pt-BR e landmark principal. GTM P629X98 em primeira
  interação ou após5s. Sete links de compra em /c/fsa, preservando offer=alt e UTM.
  Nenhum chat incluído, conforme instrução explícita do dono.
- Pipeline agora interrompe se Chrome/render não concluir ou se restar loading/
  thumbnail do bundler. Não publica React ou template quebrado como fallback.

## Validação pública final

API oficial PageSpeed, URL limpa acima, coleta 21:59:51 UTC em10/09/2026:

| Dispositivo | Desempenho | LCP | TBT | CLS |
|---|---:|---:|---:|---:|
| Celular | 92 | 3,1s | 0ms | 0,037 |
| Desktop | 96 | 0,8s | 0ms | 0,091 |

Rodada anterior às fontes Latin-ext:93/95; primeira mobile96, desktop erro da API.
Não selecionar só a maior nota. A versão final atende90 nos dois dispositivos;
notas variam e o histórico de Core Web Vitals não muda imediatamente.

Chrome390px/1440px: nove imagens carregadas, nove FAQs abrem/fecham, sete
checkouts corretos com parâmetros, offer=alt não sobrescrito, sem overflow,
sem erros JavaScript e sem falhas HTTP dos recursos da própria página. Não foram
enviadas compras nem conversões de teste. Chat ausente.

GTM por tempo e interação: uma instância, um gtm.js, pixels197461362094441 e
884049927923756 inicializados. O teste não confirmou entrega de PageView ao Meta.
Clarity herdado do GTM respondeu400 em uma navegação automatizada, mas200 em
consulta direta; sem impacto observado nas funções da página. Não foi alterada
a configuração compartilhada das tags para mascarar essa resposta externa.

Cache invalidado por prefixo da slug, incluindo campanhas/assets. URL pública
retorna200. Preview aberto no navegador do Orca e DOM conferido na URL real.
Somente /fsa foi publicada; o espelho edu existente não inclui essa nova slug.

## Manutenção

Publicar: `./publicar.sh fsa`. Reimportar a mesma fonte por
`python3 scripts/preparar-fsa.py /caminho/arquivo.html` e revisar antes do build.
Não usar esse importador específico em outra exportação sem adaptar e validar
as pré-condições. Fonte nova exige preservar FAQ, imagens, fontes e contratos
descritos em fsa/REGRAS.md. Chat continua opt-in.
