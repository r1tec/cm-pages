# Receita única — recriar páginas do WordPress como páginas leves

Uma só receita, seguida igual para as 5 slugs: **bce, drb, mce, mpg, gdp**.
Original de cada uma: `https://eduparmeggiani.com/<slug>`.
Destino: `https://contemmagia.com.br/<slug>` (pasta `<slug>/index.html` no repo).

O `coe/` é **referência de organização e otimização de código**, não de visual.
Cada página preserva o layout, o conteúdo, as imagens, os vídeos e os efeitos
**dela mesma** — só reescritos de forma leve.

---

## Quem executa

**Engenheiros de tempo de carregamento de página** — agentes cuja missão é
espremer o tempo de carregamento ao máximo (carregamento recorde, notas de
PageSpeed no teto) **mantendo 100% da fidelidade de layout**. Performance nunca
é desculpa para o menor desvio visual: se otimizar ameaça o layout, o layout
vence e a otimização se busca por outro caminho. Um por slug, contexto fresco.

## Regras de operação (valem para todos)

1. **Não parar por nada.** Travou numa decisão → consulta um **agente sênior**
   (subagente) para destravar; nunca devolve a bola pro dono no meio. O que for
   realmente insuperável **anota no relatório final** e segue.
2. **Não trazer o bruto pro contexto.** O HTML pesado do original e o JSON do
   PageSpeed são processados **fora** (sandbox/puxadinho); volta só o extrato.
3. **Baixar o original UMA vez**, salvar em disco, trabalhar do arquivo. Nunca
   rebaixar a mesma página.
4. **Reusar o pipeline existente** (`otimizar.py`, `verificar.py`,
   `publicar.sh`) — não reimplementar otimização.
5. **Relatório curto e fixo** (schema no fim). Zero prosa, zero narração.

---

## Passo a passo por slug

### 1. Copiar o original fiel
- Baixar a página `https://eduparmeggiani.com/<slug>` **completa**: HTML
  renderizado + CSS + imagens + fontes + embeds de vídeo.
- Salvar tudo em disco (fora do repo, ex.: scratchpad `originais/<slug>/`).
- Extrair e registrar, do original: **todo o texto**, a ordem e o layout das
  seções, cada **imagem** (URL/arquivo), cada **link de vídeo/embed**, o
  **link exato do botão de compra** e o **pixel** embutido (Facebook e/ou
  Google — ID e snippet).

### 2. Reescrever leve em `<slug>/index.html`
- Reconstruir a página em **HTML/CSS estático enxuto**, no padrão de
  organização do `coe/` (autocontido, sem framework, sem CDN, sem build).
- **Fidelidade é lei:** mesma sequência de seções, mesmo texto, mesmas imagens,
  mesmas cores/fontes/espaçamentos e os **efeitos da própria página**. Sem
  inventar, sem trocar imagem, sem trocar vídeo, sem trocar link.
- Preservar o **link de compra exato do original** (não padronizar para
  pay.contemmagia).
- Incluir o **pixel do próprio original** (o `otimizar.py` cuida de adiá-lo).

### 3. Pixel + carregador de slug/UTM
- Pixel: o mesmo do original, no `index.html`.
- Script de slug/UTM: portar o do `coe/` (leva as UTMs da URL atual para o
  link de checkout), **apontando o `CHECKOUT_HOST` para o host do checkout
  desta página** (o do original, não pay.contemmagia).

### 4. Publicar
- `./publicar.sh <slug>` (otimiza → confere peso/contraste → sobe por FTP →
  limpa cache do Cloudflare). Ler a saída da conferência.

### 5. Medir no PageSpeed e subir a nota
- Rodar PageSpeed Insights (via API, JSON processado fora) na URL publicada
  `https://contemmagia.com.br/<slug>`, **mobile e desktop**, capturando as 4
  categorias: **Performance, Acessibilidade, Boas Práticas (Best Practices) e
  SEO**.
- **Se qualquer nota < 97:** aplicar mais otimização possível **sem tocar no
  layout** (ex.: reduzir imagem além do padrão, ajustar contraste reprovado,
  atributos de acessibilidade que faltem, meta/SEO, adiar/dividir script),
  republicar e **remedir**. Repetir até o teto viável.
- Registrar as notas finais e, se alguma ficou < 97 mesmo após otimizar, o
  motivo (trava anotada, não parada).

### 6. Conferir fidelidade
- Comparar a página publicada com o original, seção por seção. Qualquer desvio
  visual → corrigir antes de dar a slug por pronta.

### 7. Espelhar no GitHub
- `git add -A`, commit da pasta `<slug>/`, push. (Mirror; a hospedagem é o
  resultado.)

---

## Aceite por slug

**Tem que fazer**
- Página no ar em `contemmagia.com.br/<slug>`, visualmente idêntica ao original.
- Texto, imagens, vídeos e link de compra **exatamente** os do original.
- Pixel presente e carregador de slug/UTM funcionando até o checkout.
- 4 notas do PageSpeed medidas (mobile+desktop); alvo ≥ 97 em todas.
- Cópia commitada e no GitHub.

**Não pode acontecer** (é o que pega regressão)
- Qualquer diferença visual do original (seção fora de ordem, cor/fonte/imagem
  trocada, quebra de layout no mobile).
- Trocar o link de compra, o vídeo, ou uma imagem.
- Página mais lenta que o padrão do coe / notas travadas por descuido (imagem
  não otimizada, contraste reprovado, acessibilidade faltando) que dava para
  resolver.
- Parar a esteira à espera de decisão do dono.

---

## Formato do relatório por slug (fixo, curto)

```
slug: <slug>
publicada: https://contemmagia.com.br/<slug>  (sim/não)
peso: <antes> -> <depois>
pagespeed_mobile:  perf / a11y / bestpractices / seo
pagespeed_desktop: perf / a11y / bestpractices / seo
otimizacoes_extra: <o que foi feito para passar de 97, se aplicável>
fidelidade: <ok | desvios corrigidos: ...>
travas: <nenhuma | descrição do que ficou insuperável e por quê>
commit: <hash>
```

## Ordem da esteira
bce → drb → mce → mpg → gdp. Cada slug fecha os 7 passos antes da próxima.
Ao final, um **relatório consolidado** com as 5 linhas + travas agregadas.
