# Kit do engenheiro de carregamento (por slug)

Leia junto com `docs/RECEITA-PAGINAS.md` (a receita) e `README.md` (o pipeline).
Este kit traz o que já foi descoberto do terreno — não redescubra.

## O que o pipeline faz sozinho (não refaça à mão)
Para uma página **fora do bundler** (export de WordPress/Elementor ou HTML
escrito à mão), `otimizar.py` já:
- embute o CSS e as fontes locais no `index.html` e **poda o CSS morto**;
- externaliza imagens coladas em `data:base64` para `inline-assets/`;
- recomprime as imagens do build em WebP (a pasta fonte fica intocada);
- aplica o `desempenho.json` da página (fontes, preloads, fundos, posters…);
- normaliza o carregador GTM e injeta o registro leve da visita
  (`rastreamento.py` + `rastreamento.json`);
- escreve o `.htaccess` de compressão e cache.

`preparar.py` gera o build com manifesto e cache de imagens; `--conferir` roda a
conferência visual. `verificar.py` avisa (peso de imagem, contraste), não
bloqueia. `publicar.sh` reutiliza o build atual, congela um snapshot, envia por
FTP e limpa o cache; `--build <pasta> <slug>` exige um build íntegro e atual.
Ferramentas presentes: Chrome, `cwebp`, `lftp`, credenciais no `.env`.

**Consequência:** a pasta `<slug>/` versionada guarda a página leve e legível +
`assets/` + os dois JSON de configuração. Não versione `.htaccess`, CSS embutido
à mão nem imagens já recomprimidas "na mão" — o build é derivado.

## Originais
`https://eduparmeggiani.com/<slug>/` (com barra final; sem barra dá 301).
Baixe UMA vez para o scratchpad e trabalhe do arquivo. Processe o HTML pesado
no sandbox e traga só o extrato — nunca cole o bruto no contexto.

## Rastreamento (padrão atual, 17/09/2026)
Um único carregador GTM (`GTM-P629X98`) na página — copie o do `coe/`. O pixel
do original **não** vai junto; molde de "pixel adiado escrito à mão" está
aposentado. O comportamento é escolhido por `<slug>/rastreamento.json`:

```json
{"meta_pageview_antecipado": true, "meta_envio_leve": true, "oferta": "texto:R$ 39,90"}
```

- Sem o arquivo: GTM adiado (1ª interação ou 5s) e nada mais.
- `meta_envio_leve`: PageView Meta nos primeiros ms por requisição leve a
  `facebook.com/tr`, com `_fbp`/`_fbc` em `.contemmagia.com.br`; o SDK
  (`fbevents.js`, ~215 KB) só carrega junto do GTM, com o PageView suprimido.
- `oferta`: dispara `ViuOferta` (alvo visível 1s) e habilita `Leitura30s`;
  ambos `trackCustom`, uma vez por carregamento, nos 2 pixels.
- Mais de um carregador GTM na página interrompe o build de propósito
  (evita evento duplicado).

Regressões: `scripts/testar-rastreamento.py`, `scripts/testar-meta-leve.cjs`,
`scripts/testar-meta-antecipado.cjs`. Histórico e medições:
`docs/REVISAO-TRACKING-PERFORMANCE-2026-09-17.md`.

## `desempenho.json` — o lugar dos ajustes de carregamento
Chaves em uso hoje (exemplos reais em `bce/`, `drb/`, `ecm-26/`):
- `fontes`: `{familia, peso, arquivo, inline, preload}` — com
  `preload_fontes_seletivo: true`, só as fontes comprovadas na abertura recebem
  preload; as outras perdem o preload antigo.
- `preload_imagens`: LCP com `fetchpriority="high"`.
- `reservar_dimensoes_imagens`: injeta `width`/`height` reais (corta CLS).
- `imagens_responsivas`: `{arquivo, qualidade, sizes}` gera variantes.
- `fundos_adiados`: seletores (aceita `::before`/`::after`) cujo
  `background-image` só carrega a 600px da tela.
- `posters_adiados`: adia as capas de `<video>` pelo mesmo observador.
- `fundo_acordeao`: cor de fundo do acordeão Elementor.

Valor inválido derruba o build com mensagem — é proposital.

## Checklist do HTML (já nasça com tudo isto)
- `<html lang="pt-BR">` (não en-US).
- `role="main"` no container raiz do conteúdo.
- Emojis: troque `<img class="emoji">` do CDN s.w.org pelo caractere do `alt`.
- `<video preload="none">` (corta megabytes de metadata).
- Toda `<img>` com `width` e `height` explícitos.
- **Contraste:** quando o tom reprovado é a cor da marca (os verdes) usada no
  botão de compra, repintar quebra fidelidade — mantenha e anote como trava.
  Só ajuste quando dá para escurecer sem virar "outra cor" perceptível.
- **CUIDADO com caminho relativo no CSS:** em `<slug>/assets/styles.css` os
  `url()` resolvem relativo a `assets/` — a capa é `url(diario.webp)`, nunca
  `url(assets/diario.webp)`. No `index.html` o certo é `assets/diario.webp`.
  Bug real que afundou o LCP da drb (8,5s → 2,8s).
- MEÇA em `https://contemmagia.com.br/<slug>/` COM BARRA FINAL.

## PageSpeed (só quando o pedido é de desempenho)
`medir.py` consulta a API; `afinar.sh` publica e mede em rodadas limitadas. Sem
eles: `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=<URL>&strategy=mobile`
(+ `&category=...`), JSON processado no sandbox, só as notas voltam.
PageSpeed público exige a página no ar — e publicar exige pedido.

## Patamar conhecido (celular, 17/09/2026, 1 amostra)
Depois do envio leve nas 8 páginas: DRB 97, BPV 98, COE 94, MPG 83, GDP 81,
BCE 78, ECM-26 74, MCE 73. Antes de qualquer Meta antecipado, o lote media
96–100 — o custo dominante restante ainda é o SDK da Meta carregado cedo onde
isso ainda acontece, não o CSS do Elementor.

Travas estruturais que permanecem:
- **acessibilidade ~94:** contraste dos verdes da marca (preservado por fidelidade).
- **best practices:** cookies de terceiro do GTM, exigido pelo negócio.
- CSS do Elementor (~200 KB) ainda pesa nas páginas migradas, mesmo podado.

## Regra de ouro
Fidelidade é lei. Performance nunca justifica desvio visual. Decisão técnica é
sua; escolha de negócio (texto, oferta, checkout, publicar) é do dono.
