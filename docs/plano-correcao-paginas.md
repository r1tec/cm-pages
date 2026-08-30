# Plano de correção — páginas bce/drb/mce/mpg/gdp

As 5 páginas foram publicadas, mas com **erro primário**: os fundos de imagem dos
containers do Elementor (hero de topo e cartões "presente") **não aparecem — ficam
pretos**. Texto e `<img>` renderizam; só o `background-image` de container falha.
A conferência antiga (contagem de seção + headless) não pegou isso. Corrigido só
quando um **navegador de verdade** confirma que cada fundo PINTA.

Evidência (bce, no ar): `<img>` ok (5/5), mas só **1 de ~6** `background-image`
de container pinta (só a foto de topo); aula/altar/tmpp/edu/textura = `none`.
Ferramenta de prova: `docs/tools/conferir-render.mjs <url> [saida.png]`.

## Causa-raiz a fechar (lead forte)
A regra `.elementor-element-<id>{background-image:url(x.webp);background-size:cover}`
existe e é global, arquivo retorna 200, mas o navegador computa `none` para quase
todos. O que funciona (foto de topo) NÃO tem `background-size:cover`; os quebrados
TÊM. O agente confirma com `CSS.getMatchedStylesForNode` (CDP) num container que
funciona vs. um quebrado, acha o que anula, e corrige na fonte — de forma que o
verificador passe (todos os fundos pintando).

## Esteira de correção (uma slug por vez, contexto fresco, revisor em Fable)
Ordem: **bce primeiro** (fecha a causa-raiz e o padrão de correção) → depois drb,
mce, mpg, gdp aplicando o mesmo conserto.

Por slug:
1. **Anti-quebra ANTES:** rodar `conferir-render.mjs` na página no ar e guardar o
   estado (quantos fundos pintam, imgs quebradas) + screenshot.
2. **Corrigir os fundos** na fonte (CSS/HTML da pasta), sem tocar no layout, até o
   verificador mostrar **100% dos fundos pintando** e **0 img quebrada**.
3. **Contraste (agora liberado):** escurecer minimamente os tons reprovados
   (mesma família de cor) até acessibilidade ≥ 97, incluindo o verde dos títulos.
   Repintar só o necessário; comparar com o original para não virar "outra cor".
4. **Performance mobile (77 é inaceitável):** atacar render-blocking do CSS do
   Elementor (extrair/inline do CSS crítico da 1ª dobra e adiar o resto), enxugar
   CSS não usado, confirmar preload da capa, e reavaliar o disparo do pixel para
   não competir com o LCP. Alvo: subir o mobile bem acima de 77 sem quebrar nada.
5. **Anti-quebra DEPOIS + PageSpeed:** rerodar o verificador (prova em screenshot
   lado a lado com o original) e o Lighthouse mobile+desktop. Só fecha se os
   fundos pintam, nada quebrou, e as notas subiram.
6. **Revisão em Fable** (revisor dedicado) confirmando fidelidade pixel-a-pixel
   contra o original antes de dar a slug por pronta.
7. Publicar, medir, commit, push.

## ACEITE

**Tem que fazer**
- Todo `background-image` de container PINTA na página no ar (prova no verificador).
- Toda `<img>` carrega (naturalWidth > 0) após rolagem.
- Acessibilidade ≥ 97 (contraste corrigido no mesmo tom).
- Performance mobile substancialmente acima de 77 (meta: ≥ 90 quando viável).
- Fidelidade pixel-a-pixel confirmada por revisor em Fable, com screenshot.
- Link de compra, vídeos, pixel e UTM intactos.

**Não pode acontecer** (pega regressão)
- Fundo de container preto/vazio (o erro atual) sobrando em qualquer página.
- Imagem/vídeo/link trocado ou quebrado.
- Contraste "corrigido" virando uma cor perceptivelmente diferente da marca.
- Fechar uma slug sem a prova do verificador + screenshot (nunca mais "fidelidade
  ok" sem evidência de navegador real).
- Perf mobile continuar em ~77 por falta de ataque ao CSS render-blocking.

## Nota de execução
Não rodar as 5 numa sessão só. bce fecha a causa-raiz; as outras 4 seguem o padrão
em sessões/agentes seguintes. Construção em agente de contexto fresco; revisão em Fable.
