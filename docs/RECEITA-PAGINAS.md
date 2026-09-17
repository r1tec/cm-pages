# Receita — migrar uma página do WordPress para o cm-pages

Recriar a página de `https://eduparmeggiani.com/<slug>/` como página leve em
`<slug>/index.html`, publicada em `https://contemmagia.com.br/<slug>/`.

Usada nas 5 primeiras (bce, drb, mce, mpg, gdp) e na BPV; vale para as próximas.
O `coe/` é referência de **organização de código**, não de visual: cada página
preserva o layout, o conteúdo, as imagens, os vídeos e os efeitos dela mesma.

Leia junto: `CLAUDE.md` (canônico), `docs/engenheiro-kit.md` (o terreno já
descoberto) e, quando existir, `<slug>/REGRAS.md`.

---

## Regras de operação

1. **Fidelidade é lei.** Mesmo texto, mesmas imagens, mesmos vídeos, mesmas
   cores/fontes/espaçamentos, mesma ordem de seções, os efeitos da própria
   página. Performance nunca justifica desvio visual.
2. **Baixar o original UMA vez**, salvar no scratchpad, trabalhar do arquivo.
   HTML pesado e JSON de PageSpeed se processam fora do contexto; volta o extrato.
3. **Reusar o pipeline** (`preparar.py`, `otimizar.py`, `verificar.py`,
   `publicar.sh`, `rastreamento.py`) — não reimplementar otimização nem pixel.
4. **Publicar só com pedido do dono** aplicável à tarefa. Preparar, conferir e
   medir localmente não autorizam pôr no ar (CLAUDE.md).
5. Travou numa decisão técnica: decida e registre. Só volte ao dono no que for
   escolha dele (texto, oferta, checkout, publicação).

---

## Passo a passo

### 1. Copiar o original fiel
Baixar `https://eduparmeggiani.com/<slug>/` **com barra final** (sem barra dá
301), completa: HTML renderizado, CSS, imagens, fontes e embeds de vídeo, para
`originais/<slug>/` no scratchpad. Registrar: todo o texto, a ordem das seções,
cada imagem, cada vídeo/embed, o **link exato do botão de compra** e o
rastreamento embutido no original (só como inventário — o que vai para a página
nova é o padrão do repo, item 3).

### 2. Reescrever leve em `<slug>/index.html`
HTML/CSS estático enxuto, autocontido, sem framework, sem CDN, sem build, no
padrão de organização do `coe/`. Imagens e fontes em `assets/`.

Não escreva à mão o que o pipeline faz: `.htaccess`, embutir CSS/fontes,
externalizar imagens coladas em base64, recomprimir WebP, preload de fonte e de
imagem, adiar fundos e posters. Isso sai de `otimizar.py` + `desempenho.json`
(ver kit). A pasta versionada guarda o **original leve**; o build é derivado.

Checklist mínimo do HTML: `<html lang="pt-BR">`, `role="main"` no container do
conteúdo, `<img>` com `width`/`height`, `<video preload="none">`, emoji como
caractere (não `<img>` do CDN s.w.org).

### 3. Rastreamento: um GTM + `rastreamento.json`
A página nova **não leva o pixel do original**. Ela nasce com o carregador GTM
conhecido do repo (`GTM-P629X98`) — copie o bloco do `coe/index.html`. Com
exatamente um carregador na página, `rastreamento.py` assume o resto no build:
adia o GTM para a 1ª interação ou 5s e, quando a página tem `rastreamento.json`,
injeta o registro leve da visita.

`<slug>/rastreamento.json` (padrão atual das 8 páginas no ar):

```json
{
  "meta_pageview_antecipado": true,
  "meta_envio_leve": true,
  "oferta": "texto:R$ 39,90"
}
```

- `meta_pageview_antecipado`: PageView Meta registrado no início, sem o SDK.
- `meta_envio_leve`: envia por requisição leve a `facebook.com/tr`, criando
  `_fbp`/`_fbc` em `.contemmagia.com.br`; o SDK completo só entra com o GTM.
- `oferta`: alvo do evento `ViuOferta` (com `Leitura30s`, alimenta remarketing).
  Sem esse campo, a página não gera sinal de engajamento.

Reversão é editar o JSON e republicar. Arquivo inválido interrompe o build.

### 4. Checkout e UTM
Destino padrão: `https://pay.contemmagia.com.br/c/<slug>` (é o que as 8 páginas
publicadas usam), salvo se o pedido indicar outro checkout. Porte o script de
slug/UTM do `coe/` apontando `H` para o host usado, para repassar UTMs e
`fbclid` até o checkout. Confira os links no preview antes de fechar.

### 5. Preparar e conferir
`python3 preparar.py <slug> --saida /tmp/preview-<slug> --conferir`.
Abrir o preview em celular e desktop: fidelidade seção a seção contra o
original, imagens e fundos, overflow, FAQ, vídeos e CTAs. Interação nova se
exercita no preview — screenshot não prova comportamento.

Regressões do rastreamento: `python3 scripts/testar-rastreamento.py`
(e `scripts/testar-meta-leve.cjs` quando mexer no envio leve).

### 6. Desempenho
Use a skill `otimizar` quando o pedido for de desempenho ou houver impacto
concreto. Ajustes entram por `<slug>/desempenho.json` (fontes, preload de
imagem, `fundos_adiados`, `posters_adiados`, `imagens_responsivas`), não
editando o HTML à mão. Meta de nota vem do pedido; não perseguir 100 constante.
PageSpeed público exige a página no ar — sem autorização, medir localmente e
distinguir Lighthouse local de medição pública.

### 7. Publicar (só com pedido)
`./publicar.sh <slug>` ou `./publicar.sh --build /tmp/preview-<slug> <slug>`
para enviar exatamente o build já conferido. Troca restrita só do script de
rastreamento (sem rebuild): `./publicar.sh --gtm-performance --meta-antecipado
--aplicar <slug>` — sempre pelo `publicar.sh`, não chamando `alinhar_gtm.py`
direto. Depois de publicar, conferir a URL real com barra final.

### 8. Versionar
Commit e push só dos arquivos da tarefa (`<slug>/` e o doc que registrou a
migração), em português, direto na `main`. Nada de `git add -A`.

---

## Aceite por slug

**Tem que fazer**
- Página visualmente idêntica ao original, em celular e desktop.
- Texto, imagens, vídeos e link de compra exatamente os definidos no pedido.
- Um único carregador GTM, `rastreamento.json` presente e visita registrada uma
  vez por pixel; UTMs e `fbclid` chegando ao checkout.
- Preview conferido com interações exercitadas; testes de rastreamento verdes.
- Cópia commitada.

**Não pode acontecer**
- Diferença visual do original (seção fora de ordem, cor/fonte/imagem trocada,
  quebra no mobile).
- Trocar link de compra, vídeo ou imagem sem pedido.
- Dois carregadores GTM ou PageView duplicado.
- Pixel do original solto na página, fora do padrão do repo.
- Publicar sem pedido, ou publicar build diferente do conferido.

---

## Relatório por slug (curto)

```
slug: <slug>
preview: <caminho>     publicada: <url ou não>
peso: <antes> -> <depois>
rastreamento: <1 GTM | envio leve sim/não | oferta: ...>
desempenho: <medições feitas, se houve pedido>
fidelidade: <ok | desvios corrigidos: ...>
travas: <nenhuma | o que ficou e por quê>
commit: <hash>
```
