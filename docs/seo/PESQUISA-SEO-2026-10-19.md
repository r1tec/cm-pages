# Pesquisa: SEO orgânico para páginas de venda da Contém Magia

Data: 19/10/2026. Fontes: documentação oficial do Google (Search Central, ajuda do Search Console e do Google Ads) primeiro; depois estudos da Ahrefs, Backlinko, Zyppy e Search Engine Land. Marquei como **[inferência]** o que é conclusão minha, sem fonte que diga isso diretamente.

---

## 0. Achado urgente: o domínio está bloqueando o Google hoje

Conferido em 19/10/2026 com `curl`:

| URL | Status |
|---|---|
| `https://contemmagia.com.br/robots.txt` | **500** (user-agent de navegador e de Googlebot); o corpo é uma página "403 Forbidden" do LiteSpeed; requisição HEAD dá 403 via Cloudflare |
| `https://contemmagia.com.br/` (home) | **500** com user-agent de navegador; 403 com user-agent curto |
| `/sitemap.xml`, `/sitemap_index.xml`, `/wp-sitemap.xml` | **500** |
| `https://contemmagia.com.br/drb/` | 200 |

O Google trata assim um robots.txt que responde 5xx ([Google: robots.txt, atualizado em 31/08/2026](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt)):
- **primeiras 12 h:** o Google **para de rastrear o site** e continua tentando buscar o robots.txt;
- **próximos 30 dias:** usa a última versão boa que tiver em cache; se não houver nenhuma, entende que não há restrição;
- **depois de 30 dias:** se o site em geral estiver disponível, trata como se não existisse robots.txt; **se o site tiver problema geral de disponibilidade, para de rastrear** e só volta a pedir o robots.txt de tempos em tempos.

Como a home também dá 500, o domínio pode estar caindo no segundo caso (**[inferência]**: vale confirmar no relatório de rastreamento do Search Console). Isso precisa ser resolvido **antes de qualquer outro trabalho de SEO**. Resposta 4xx (menos 429) seria tratada como "não existe robots.txt, pode rastrear tudo" (mesma fonte). Ou seja, **um 404 é inofensivo; o 500 bloqueia**.

Sitemap: se a busca falha, "o Google vai tentar de novo por alguns dias e depois para, se o sitemap continuar indisponível". Depois de corrigir, é preciso reenviar ([Ajuda do Search Console: relatório de sitemaps](https://support.google.com/webmasters/answer/7451001?hl=en)).

Observações sobre `/drb/` (não era o foco, mas aparecem no HTML servido): tem **2 `<h1>`**; o título era "DRB – Diário de Rezas e Benzimentos – **V3** – Contém Magia"; não tinha tags `og:`; a meta description dizia "Caderno de Rez**os**". (Correção da sessão: a `/drb/` é HTML estático do cm-pages; as classes `elementor-*` são herança da migração do WordPress. Título, descrição e `og:` foram corrigidos e publicados em 19/10/2026 — ver `docs/PLANO-SEO.md`.)

---

## 1. O que faz uma página de venda ranquear

**Intenção de busca manda.** A Ahrefs recomenda olhar os "3 Cs" do que já ranqueia para o termo: **tipo** de conteúdo (post, página de produto, landing page), **formato** (guia, lista, comparação) e **ângulo**, e seguir o padrão dominante ([Ahrefs: Search intent](https://ahrefs.com/blog/search-intent/)). O próprio Google diz que o conteúdo precisa ser feito "primeiro para pessoas" e satisfazer quem chega pela busca ([Google: conteúdo útil e confiável](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)).

Consequência prática **[inferência, apoiada nas fontes acima]**:
- **A página de venda longa ranqueia para buscas de marca e transacionais**: "diário de rezas e benzimentos", "curso de benzimento online", "apostila de rezas pdf", "contém magia benzimento".
- **Buscas informativas** ("reza contra mau olhado", "como benzer criança") são ganhas por artigos/guias. Uma página de venda dificilmente entra nessas SERPs, porque o tipo de conteúdo não corresponde.
- Além disso, consultas informativas são as mais afetadas pelos AI Overviews. A Ahrefs mediu queda de cerca de 34,5% no CTR da posição 1 quando há AI Overview ([Ahrefs: AI Overviews reduce clicks](https://ahrefs.com/blog/ai-overviews-reduce-clicks/)). Isso reduz o ganho do conteúdo informativo, mas não o anula.

**Hub/cluster de conteúdo ligando à página de venda: o que existe de evidência**
- **Links internos têm o apoio mais sólido.** O estudo da Zyppy (23 milhões de links internos, cerca de 1.800 sites) achou correlação entre mais links internos e mais tráfego: URLs com 0–4 links internos tiveram em média 2 cliques; com 40–44, cerca de 4 vezes mais, com retorno incerto depois disso. **Variedade de texto âncora** se correlaciona fortemente com mais tráfego ([Zyppy: 23 Million Internal Links](https://zyppy.com/seo/internal-links-study/)). É correlação, não prova de causa.
- O Google diz que links ajudam a descobrir páginas e entender a relevância delas, e recomenda texto âncora descritivo em `<a href>` rastreável ([Google: boas práticas de links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable); [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)).
- **Números como "+43% com topic clusters" (atribuídos à HubSpot) não têm fonte primária localizável**; os outros são estudos de caso de fornecedores, sem grupo de controle. Trate cluster como **boa prática plausível, não como resultado comprovado**.

Modelo recomendado **[inferência]**: artigos no WordPress (ex.: "Reza contra mau olhado: como fazer") → link contextual com âncora variada para `/drb` → página de venda com texto indexável sobre o que o produto entrega.

---

## 2. Checklist on-page (validado)

| Item | O que fazer | Fonte |
|---|---|---|
| **`<title>`** | Um por página, **descritivo e conciso**, sem "V3", sem repetir palavras (keyword stuffing) e sem texto padrão repetido entre páginas. O Google não tem limite, mas corta pela largura do dispositivo. | [Google: title links](https://developers.google.com/search/docs/appearance/title-link) |
| Tamanho do título | Títulos de **40–60 caracteres** tiveram CTR 33,3% maior no estudo da Backlinko (correlação). Colocar o termo principal no começo ajuda a não ser cortado **[inferência]**. | [Backlinko: Google CTR stats](https://backlinko.com/google-ctr-stats) |
| Reescrita do título | O Google monta o título a partir de `<title>`, H1, `og:title`, texto em destaque e âncoras. Alinhar `<title>`, H1 e `og:title` reduz reescritas. | [Google: title links](https://developers.google.com/search/docs/appearance/title-link) |
| **Meta description** | Única por página, resumo específico. **Não é fator de ranqueamento**; influencia o CTR. O Google pode trocar por trecho da página. | [Google: snippets e meta description](https://developers.google.com/search/docs/appearance/snippet) |
| **H1 e hierarquia** | O Google não exige H1 único, mas usa o H1 como fonte do título. Use **um H1** claro com o nome do produto e H2/H3 em ordem **[boa prática; a `/drb` tem 2 H1]**. | [Google: title links](https://developers.google.com/search/docs/appearance/title-link) |
| **Texto alternativo** | `alt` descritivo, imagem perto de texto relevante, nome de arquivo descritivo (`diario-rezas-capa.webp`, não `IMG001.jpg`). | [Google: SEO de imagens](https://developers.google.com/search/docs/appearance/google-images) |
| **Texto em imagem** | O Google entende imagens pelo `alt`, pela página ao redor e por visão computacional. Texto importante (promessa, conteúdo, depoimentos) precisa estar **em HTML**. | [Google: SEO de imagens](https://developers.google.com/search/docs/appearance/google-images) |
| **URL** | Curta e descritiva ajuda o usuário. `/drb` é opaco **[inferência]**; trocar o slug exige 301 e quebraria campanhas. Não vale o risco só por SEO. | [SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide) |
| **Canonical** | `rel="canonical"` absoluto apontando para a própria URL. Útil porque os anúncios geram URLs com `?utm_…`/`?fbclid`, que viram duplicatas. | [Google: canonicalização](https://developers.google.com/search/docs/crawling-indexing/canonicalization) |
| **Open Graph** | `og:title` é uma das fontes do título no Google. `og:image` ganhou boas práticas de imagem preferida em mar/2026. A `/drb` não tem `og:`. | [Google: title links](https://developers.google.com/search/docs/appearance/title-link); [changelog](https://developers.google.com/search/updates) |
| **Links internos** | `<a href>` real com âncora descritiva; links vindos de artigos e da home. | [Google: links](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) |
| **Core Web Vitals** | "São usados pelos nossos sistemas de ranqueamento", mas bons números "não garantem" o topo, e buscar nota perfeita só por SEO "pode não ser o melhor uso do seu tempo". Peso real: **critério de desempate**, não alavanca principal. | [Google: page experience](https://developers.google.com/search/docs/appearance/page-experience) |
| HTTPS | Recomendado; faz parte da experiência. | [Google: get started / manutenção](https://developers.google.com/search/docs/fundamentals/get-started) |
| Spam | Não repetir termos de forma artificial nem listar cidades ou palavras-chave. | [Google: políticas de spam](https://developers.google.com/search/docs/essentials/spam-policies) |

---

## 3. Dados estruturados para página de produto digital/curso (estado em out/2026)

Regra geral: markup com problema pode gerar **ação manual**. Essa ação "tira a elegibilidade para resultado rico; **não afeta o ranqueamento**" ([Google: diretrizes gerais de dados estruturados](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)). O conteúdo marcado precisa estar visível na página (mesma fonte).

| Tipo | Situação | Recomendação |
|---|---|---|
| **Product + Offer** | Há dois usos. **Product snippet** (preço/estrelas no resultado) vale para páginas de produto em geral. **Merchant listing** exige que você seja o vendedor, com `Offer` e preço maior que zero, numa página onde dá para comprar e com foco em **um** produto ([merchant listing](https://developers.google.com/search/docs/appearance/structured-data/merchant-listing); [Product](https://developers.google.com/search/docs/appearance/structured-data/product)). As duas páginas **não dizem nada sobre produto digital**. O Merchant Center proíbe **e-books/PDF em anúncios do Shopping** ([política de conteúdo não suportado](https://support.google.com/merchants/answer/6150006?hl=en)). | **Usar** `Product` + `Offer` (name, description, image, price, priceCurrency=BRL, availability, url). Risco baixo se for verdadeiro. Esperar no máximo snippet com preço; experiências de Shopping para PDF são improváveis **[inferência]**. |
| **Course info** | **Descontinuado**: retirado em 12/06/2025, junto com Book Actions, ClaimReview, Estimated Salary, Learning Video, Special Announcement e Vehicle Listing; documentação removida em set/2025. "Não afeta o ranqueamento." | Não vale esforço ([blog do Google, 12/06/2025](https://developers.google.com/search/blog/2025/06/simplifying-search-results); [changelog](https://developers.google.com/search/updates)). |
| **Course list (carrossel)** | Ainda documentado (atualizado em 08/09/2026), mas **só em inglês**; exige 3+ cursos, markup de carrossel numa página resumo, sem preço ou promoção no nome; violação pode dar ação manual. | **Não se aplica** a página em português ([Google: Course list](https://developers.google.com/search/docs/appearance/structured-data/course)). |
| **FAQPage** | Restrito a sites governamentais e de saúde desde ago/2023; **descontinuado**: "deixa de aparecer na Busca a partir de 7/5/2026"; documentação removida em 15/06/2026. | O markup não dá mais resultado rico. Manter o FAQ **visível** na página (ajuda o conteúdo); o markup é opcional e inofensivo ([changelog do Google](https://developers.google.com/search/updates); [PPC Land](https://ppc.land/google-kills-faq-rich-results-what-seos-saw-coming-since-2019/)). |
| **Organization** | Suportado (logo, nome, `sameAs`). O lugar indicado é a home ou a página "Sobre". | Colocar no WordPress (home/Sobre), não em cada página de venda ([Google: Organization](https://developers.google.com/search/docs/appearance/structured-data/organization)). |
| **BreadcrumbList** | Suportado, mas desde jan/2025 **aparece só no desktop**. | Opcional, baixo ganho ([Google: breadcrumb](https://developers.google.com/search/docs/appearance/structured-data/breadcrumb)). |
| **Review / AggregateRating** | `Product` e `Course` podem ter avaliações. Regras: avaliação **visível** na página; sobre **um** item; **não agregar de outros sites**; nada de avaliação falsa ou incentivada sem aviso; recomenda-se aceitar só nota com comentário e nome do autor. **Autoavaliação:** se a entidade controla as avaliações sobre si mesma, páginas com `Organization`/`LocalBusiness` **não são elegíveis** a estrelas, inclusive via widget do Google ou Facebook. Violação pode dar ação manual. | **Risco**: depoimentos em print (imagem), copiados do Instagram/WhatsApp ou da Hotmart = conteúdo não visível em texto ou agregado de outro site. Só marcar `AggregateRating` no `Product` se as avaliações forem coletadas na própria página, em texto, com nome. **Nunca** em `Organization` ([Google: review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)). |

---

## 4. robots.txt e sitemap com erro 500: como corrigir

1. **Fazer `/robots.txt` responder 200** (ou, no mínimo, 404). O 500 vem do servidor de origem (LiteSpeed/WordPress), atrás do Cloudflare (`cf-cache-status: BYPASS`). Caminhos possíveis **[inferência; validar com a hospedagem]**:
   - colocar um arquivo físico `robots.txt` na raiz pública, para o LiteSpeed servir sem passar pelo PHP;
   - ver se alguma regra de WAF/segurança do LiteSpeed ou de plugin está bloqueando (o corpo da resposta é um "403 Forbidden" embrulhado em 500);
   - ou servir o robots.txt pelo próprio Cloudflare (regra ou Worker).
   - A home também dá 500, então o problema provavelmente é geral do WordPress, não só do arquivo.
2. Conteúdo mínimo sugerido:
   ```
   User-agent: *
   Allow: /
   Sitemap: https://contemmagia.com.br/sitemap_index.xml
   Sitemap: https://contemmagia.com.br/sitemap-paginas.xml
   ```
   A linha `Sitemap:` precisa de URL absoluta, pode aparecer várias vezes e não depende de user-agent ([Google: robots.txt](https://developers.google.com/search/docs/crawling-indexing/robots/robots_txt); [Google: criar e enviar sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)).
3. **Sitemap separado para as páginas estáticas:** pode morar em qualquer lugar, mas "a menos que seja enviado pelo Search Console, um sitemap afeta só os descendentes da pasta"; a recomendação é a **raiz**. Precisa ser UTF-8, com URLs absolutas, até 50 MB / 50 mil URLs; pode haver vários sitemaps ou um índice ([Google: build sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap)). Plano prático: `https://contemmagia.com.br/sitemap-paginas.xml` gerado pelo `preparar.py`/`publicar.sh`, listando só as URLs canônicas com `<lastmod>`, declarado no robots.txt **e** enviado no Search Console.
4. Depois de corrigir: reenviar os sitemaps no relatório de Sitemaps (status "Success") e conferir o robots.txt em Configurações → robots.txt no Search Console ([Ajuda: sitemaps](https://support.google.com/webmasters/answer/7451001?hl=en)).

---

## 5. Search Console

- **Propriedade de domínio** (`contemmagia.com.br`, cobre http/https e todos os subdomínios) **exige verificação por DNS** (registro TXT). Verificar o domínio raiz verifica automaticamente os subdomínios ([Ajuda: verificar propriedade](https://support.google.com/webmasters/answer/9008080?hl=en)).
- **No Cloudflare:** o assistente do Search Console reconhece o Cloudflare e pode **adicionar o TXT sozinho** depois de você autorizar. Manualmente: DNS → Add record → Tipo **TXT**, Nome **@**, Conteúdo = `google-site-verification=…` → salvar → "Verificar". **Não apague o TXT depois**, porque o Google confere de tempos em tempos e a propriedade expira ([guia Glitter](https://www.glitter.io/guides/how-to-set-up-a-google-search-console-profile-step-by-step-guide); [Ajuda: verificação](https://support.google.com/webmasters/answer/9008080?hl=en)).
- **Sitemap:** Indexação → Sitemaps → colar a URL → Enviar. "Discovered pages" não garante indexação; dá para filtrar o relatório de Indexação por sitemap ([Ajuda: sitemaps](https://support.google.com/webmasters/answer/7451001?hl=en)).
- **Inspeção de URL / Solicitar indexação:** inspecionar a URL → "Testar URL publicada" → "Solicitar indexação". Normalmente leva cerca de 1 dia, às vezes até 1–2 semanas; **não garante** indexação; tem **limite diário**. Para muitas URLs, use sitemap com `<lastmod>` ([Ajuda: URL Inspection](https://support.google.com/webmasters/answer/9012289?hl=en)).

---

## 6. O nicho espiritual é YMYL? Cuidados com E-E-A-T

- As diretrizes de avaliadores definem YMYL pelo **risco de dano**: temas que podem afetar a **saúde, a estabilidade financeira ou a segurança** das pessoas, ou o bem-estar da sociedade. A revisão de 11/09/2025 foi pequena e "não muda a orientação de avaliação" ([Search Engine Land, set/2025](https://searchengineland.com/google-updates-search-quality-raters-guidelines-adding-ai-overview-examples-ymyl-definitions-461908); [PDF das diretrizes](https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf)). As notas dos avaliadores não alteram o ranqueamento diretamente (mesma reportagem).
- **[inferência]** Espiritualidade em si **não é YMYL**. O texto **vira YMYL** quando promete cura de doença ("benzimento cura…"), substitui tratamento médico, promete dinheiro ("abre caminhos financeiros") ou trata de segurança. Benzimento para criança doente, depressão ou ansiedade fica no limite. Nesses pontos: linguagem de tradição e experiência, sem promessa de resultado de saúde ou dinheiro, e com aviso de que não substitui atendimento médico.
- **E-E-A-T na prática** ([Google: conteúdo útil, "Quem, Como e Por quê"](https://developers.google.com/search/docs/fundamentals/creating-helpful-content)):
  - deixar claro **quem** criou o conteúdo, com assinatura que leve a uma página com a trajetória da professora (anos de prática, linhagem, formação, fotos reais);
  - página **"Sobre"** da escola, ligada ao `Organization` com `sameAs` (Instagram, YouTube);
  - **experiência em primeira mão** (o "E" a mais) pesa num nicho de tradição oral;
  - **nunca** inventar perfil, credencial ou foto gerada por IA: o Google chama isso de "engano" e "sinal de página de baixa qualidade".

---

## 7. Pesquisa de palavra-chave sem ferramenta paga

Método (cerca de 2 h por produto):
1. **Sementes:** liste 5–10 termos do produto ("reza", "benzimento", "oração de proteção", "mau olhado", "quebranto", "simpatia").
2. **Google Autocomplete:** em aba anônima, com localização Brasil, digite a semente + cada letra (a–z) e + "como", "para", "pdf", "curso". As previsões refletem buscas reais e frequentes ([Google: como funciona o autocomplete](https://blog.google/products/search/how-google-autocomplete-works-search/)).
3. **"As pessoas também perguntam" e "Pesquisas relacionadas":** abra 3–4 perguntas (cada uma gera outras) e anote. Isso vira títulos de artigos e H2.
4. **Google Trends** (Brasil, 5 anos): compare termos ("benzimento" × "benzedeira" × "reza"). Os valores são **relativos** (0–100), não volume absoluto. Use para escolher a palavra e ver sazonalidade e estados ([Ajuda do Trends](https://support.google.com/trends/answer/4365533?hl=pt-BR)).
5. **Keyword Planner (Google Ads, grátis):** o Google diz que "é preciso informar o faturamento e concluir a configuração da conta" para ter sugestões de palavras ([Ajuda Google Ads: Keyword Planner](https://support.google.com/google-ads/answer/7337243?hl=en)). Não precisa veicular anúncio; sem gasto, o volume aparece **em faixas** (ex.: 1 mil–10 mil) ([Rank Math](https://rankmath.com/kb/use-keyword-planner-without-running-ads/)).
6. **Classifique a intenção olhando a SERP real** (os 3 Cs da Ahrefs). Se aparecem artigos, faça artigo; se aparecem lojas/Hotmart, a página de venda pode competir.
7. **Depois que o site estiver no ar:** o relatório de Desempenho do Search Console mostra as consultas reais em que as páginas já aparecem. É a melhor fonte grátis.

---

## 8. Prazos realistas

- Google: "algumas mudanças fazem efeito em poucas horas, outras podem levar **vários meses**"; espere **algumas semanas** para avaliar ([SEO Starter Guide](https://developers.google.com/search/docs/fundamentals/seo-starter-guide)). Mudanças de título levam de dias a semanas para serem reprocessadas ([title links](https://developers.google.com/search/docs/appearance/title-link)).
- Indexação após solicitar: cerca de 1 dia, até 1–2 semanas ([URL Inspection](https://support.google.com/webmasters/answer/9012289?hl=en)).
- Ahrefs (2025; amostra de URLs de 2023): só **1,74%** das páginas novas chegam ao top 10 em 1 ano (6,11% num recorte só de conteúdo em inglês não vazio). Das que chegam, **40,82% chegam no 1º mês**. Se depois de ~6 meses não estiver no top 10, as chances caem e vale revisar. **72,9%** do top 10 tem mais de 3 anos, e a página média em 1º lugar tem **5 anos** ([Ahrefs: How long does it take to rank](https://ahrefs.com/blog/how-long-does-it-take-to-rank/)).
- **Expectativa [inferência]:** termos de marca e de cauda longa transacional, em semanas depois de indexar; termos informativos com concorrência, de 3 a 12 meses e só com conteúdo e links internos. Nada acontece enquanto o robots.txt e a home derem 500.

---

## Ordem sugerida

1. Corrigir o 500 do robots.txt e da home (bloqueador).
2. Verificar a propriedade de domínio no Search Console via TXT no Cloudflare.
3. Sitemap das páginas estáticas na raiz, declarado no robots.txt e enviado.
4. On-page das páginas de venda: título limpo, 1 H1, `og:`, canonical, texto indexável, `Product`+`Offer`.
5. Página "Sobre" e autoria da professora, com `Organization` no WordPress.
6. Pesquisa de palavras-chave, depois artigos informativos ligando às páginas de venda.
