# Handoff — páginas bce/drb/mce/mpg/gdp

Estado em 2026-08-30. Fio para continuar em sessão nova.

## Situação atual (tudo no ar e verificado)
As 5 páginas foram recriadas do WordPress como estáticas leves e estão publicadas
em `contemmagia.com.br/<slug>/`, commitadas e no GitHub (main). Últimos commits:
bce/perf, drb `cc1bd67`, consolidado `b4a98a2`.

Placar ao vivo (Lighthouse real):

| slug | fundos | mobile perf/a11y/bp/seo | desktop |
|------|--------|--------------------------|---------|
| bce | 5/5 | 78 / 98 / 73 / 100 | 99 / 98 / 96 / 100 |
| drb | 6/6 | 84 / 98 / 73 / 100 | 100 / 98 / 96 / 100 |
| mce | 9/9 | 75 / 98 / 77 / 100 | 100 / 98 / 100 / 100 |
| mpg | 8/8 | 85 / 98 / 77 / 100 | 98 / 98 / 100 / 100 |
| gdp | 5/5 | 80 / 98 / 77 / 100 | 99 / 98 / 100 / 100 |

Cada uma: texto/imagens/vídeos/link de compra do original, pixel GTM-P629X98
adiado, carregador de UTM até `pay.contemmagia.com.br/c/<slug>`.

## Como as coisas funcionam aqui
- **Publicar:** `./publicar.sh <slug>` (otimiza → confere → FTP → limpa cache CF).
  Credenciais no `.env`. Permissões já liberadas em `.claude/settings.local.json`.
- **Portão anti-quebra (OBRIGATÓRIO antes de fechar qualquer página):**
  `node docs/tools/conferir-render.mjs https://contemmagia.com.br/<slug>/ /tmp/x.png`
  Reprova se algum `background-image` de container não pintar ou `<img>` não carregar.
  Fundos em `::before` não são contados pela ferramenta — confirmar por CDP/screenshot.
- **PageSpeed:** a API pública sem chave estourou cota. Usar Lighthouse local:
  `npx lighthouse <url> --form-factor=mobile --screenEmulation.mobile ...`.
  Medir SEMPRE com barra final (`/<slug>/`) — sem barra é 301 e perde ~1s.
- **Regras/kit:** `docs/receita-paginas.md` (a receita), `docs/engenheiro-kit.md`
  (checklist técnico + bugs já conhecidos), `docs/plano-correcao-paginas.md`.

## O bug central já resolvido (não reintroduzir)
O Elementor tem 3 regras que apagam o fundo dos containers do 4º em diante
(`.e-con.e-parent:nth-of-type(n+4):not(.e-lazyloaded)…{background-image:none!important}`
+ variantes n+3/n+2 em `@media max-height`). Só o JS do WordPress adiciona
`.e-lazyloaded`; na versão estática ele não existe → fundo preto. **Foram removidas
das 5.** Qualquer página nova do Elementor terá isso — buscar `e-lazyloaded` e remover.

## Aberto (decisões do dono / próximos passos)
1. **Mobile 75-85, não ≥90.** Teto é o pixel do GTM (~570KB de JS de terceiro).
   Subir de verdade exige **atrasar/remover o pixel** — decisão de rastreamento do dono,
   ainda NÃO autorizada. A conversão da capa para `<img>` já foi feita onde ajudava.
2. **Acessibilidade 98, não 100.** Falta só `heading-order` (ordem de títulos herdada
   do original). Corrigir mexe em tags de heading e arrisca o visual — não feito por fidelidade.
3. **best-practices mobile 73-77.** Cookies de terceiro do GTM. Estrutural com o pixel.

## Dívida técnica desta sessão
- O commit `cc1bd67` (mensagem "drb") varreu, por um `git add -A` durante agentes
  paralelos, arquivos de mce/mpg/gdp. O ESTADO FINAL em disco/HEAD está correto e
  consistente com o que está no ar; só o histórico ficou misturado. Se for limpar,
  é `rebase` cosmético — sem urgência.
- Ao rodar correções em paralelo, **commitar escopado** (`git add <slug>/`), nunca `-A`.

## Regra de ouro para quem continuar
Nenhuma página fecha sem: (a) `conferir-render.mjs` na URL no ar mostrando todos os
fundos pintando e 0 img quebrada, (b) screenshot comparado ao original, (c) Lighthouse.
Contagem de seção/headless NÃO é prova de fidelidade — foi assim que passou imagem preta.
