---
name: seo
description: Prepara o SEO de uma página do cm-pages — pesquisa das palavras que a persona busca, título e descrição com gancho de curiosidade, imagem de compartilhamento, dados de produto e entrada no sitemap. Use em toda página nova (chamada pela preparar-pagina) e quando o dono pedir SEO, Google, busca orgânica ou "aparecer no Google". Não muda texto visível da página.
---

# SEO da página

Método, evidências e limites: `docs/PLANO-SEO.md` (leia "Como escolher as
palavras" e "Builds"); fontes em `docs/seo/`. O SEO mora em `<slug>/seo.json`,
aplicado pelo `seo.py` dentro do `preparar.py`: nunca edite título, descrição,
`og:` ou JSON-LD à mão no HTML — o build troca tudo pelo `seo.json`.

## Passos

1. **Fatos da página primeiro.** Do build (`.build/<slug>/index.html`): nome
   exato do produto, promessa do H1, formato (PDF, curso, aula), preço que
   aparece escrito ("R$ 39,90"), autor citado. Só entra no SEO o que a página
   já afirma.
2. **Palavras reais.** `python3 scripts/palavras_chave.py "<tema>" "<tema> pdf"
   "como <verbo> <tema>" "<produto> edu parmeggiani" …` (10–30 sementes).
   Separe em três camadas — **compra** (já quer o produto: "guia de …",
   "… pdf", "curso de …"), **marca** (procura o nome do produto/autor) e
   **curiosidade** (dor da persona: "reza contra mau olhado"). Use a grafia que
   as pessoas buscam (ex.: "pomba gira" além de "Pombogira").
3. **`<slug>/seo.json`:**
   - `titulo`: 40–60 caracteres, palavra de compra no começo, nome do produto,
     sem código interno ("V3", "DRB");
   - `descricao`: 140–160, abre com o gancho de curiosidade da persona e fecha
     com o formato; nada de prometer cura, dinheiro ou resultado garantido;
   - `produto`, `preco` ("39.90", o valor à vista escrito na página; o build
     recusa preço que a página não mostra), `imagem`
     (`assets/og-<slug>.jpg`) e `imagem_alt`.
4. **Imagem de compartilhamento:** `python3 scripts/og_imagem.py <slug>
   <imagem>`. Prefira foto ou capa/mockup do produto; arte só de letras sai
   ruim. Olhe o resultado antes de seguir.
5. **Build e conferência:** `python3 preparar.py <slug>`; confira no build um
   `<title>`, uma descrição, um canonical, um `Product`, e que o corpo da
   página não mudou.
6. **Sitemap e home:** inclua a página em `config/raiz/paginas.json` (variações
   de teste e eventos encerrados ficam fora) e rode `python3 raiz.py --publicar`
   quando publicar — ele também avisa Bing e outros buscadores (IndexNow). O
   rótulo de venda orgânica (`utm_medium=organic` para visita de buscador) entra
   sozinho com o `seo.json`; o botão de compra precisa repassar a URL ao checkout,
   como as páginas atuais já fazem.
7. **Publicar** segue a skill `publicar`. Depois, no Search Console (quando
   ligado), peça indexação da URL nova.

## Não fazer

- Marcar avaliações/estrelas a partir de depoimentos em imagem ou de outros
  sites (risco de punição manual); FAQ marcado não aparece mais no Google.
- Trocar slug por SEO (quebra campanhas).
- Republicar página cujo build diverge do que está no ar sem conferir o corpo
  contra a versão publicada (caso `coe` em 19/10/2026: a página no ar veio de
  versão antiga do pipeline; o SEO foi aplicado sobre o HTML publicado).
