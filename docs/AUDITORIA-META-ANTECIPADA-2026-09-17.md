# Auditoria Meta antecipada — 17/09/2026

Pedido: conferir se o padrão da DRB (pixel cedo, GTM por interação/5s, sem
PageView duplicado) funciona e está em todas as páginas. Fora: ECM-26-v1 e FSA.

## Resultado no ar (Chrome real, envios à Meta/Google abortados no teste)

- DRB, MCE, BCE, MPG, COE, GDP, BPV: carregador idêntico ao `meta-pageview-antecipado.js`,
  um único GTM, GTM em ~5s parado / ~2s com rolagem. Biblioteca Meta em 0,1–1s.
- URL sem parâmetros: 1 PageView por pixel e nenhum repetido após o GTM em DRB, MCE, BCE,
  MPG, COE e GDP. Sem erros JS.
- ECM-26 não tinha o padrão: pixel só vinha pelo GTM (2,6–7s). Opt-in criado em
  `ecm-26/rastreamento.json` e build `.build/ecm-26` testado: biblioteca em ~27ms, contagem
  interna 1 PageView por pixel após GTM, sem erros, textos e links iguais ao público
  (só o cronômetro difere). **Não publicado.** `ecm-26/index.html` tem alteração local
  anterior não commitada que iria junto.

## Bloqueador: visitas perdidas por política de segurança

O pixel envia por GET quando o pacote cabe em ~2.048 caracteres; acima disso usa
formulário em iframe para `www.facebook.com/tr`. O cabeçalho do domínio
`Content-Security-Policy: frame-ancestors 'self'; frame-src 'self' https://clkdmg.site`
bloqueia esse iframe.

- BPV: bloqueado sempre (metatags og/twitter somam ~470 caracteres no pacote; 2.469 no total).
- Todas as demais: bloqueado com link de campanha realista (UTMs com nome|ID + fbclid).
  Pacote base ~1.100–1.500; sobra ~550 caracteres para a URL.
- O pixel conta o evento internamente, mas nada sai do navegador. Não é regressão do
  padrão antecipado: o GTM usa o mesmo transporte.

Origem confirmada (17/09): as respostas são as páginas estáticas novas (carregador Meta e chat
novos presentes; "elementor" só como nome de classe herdado). O cabeçalho sai do servidor de
origem em resposta nova (cache MISS), só para HTML/PHP; imagens não recebem. Vem do bloco
`# BEGIN HttpHeaders` em `/public_html/.htaccess`, resto de plugin do WordPress antigo, que
vale para toda pasta publicada abaixo dele, inclusive as oito slugs em tráfego. Correção sugerida: incluir `https://www.facebook.com` em
`frame-src` no plugin, preservando `clkdmg.site`; depois repetir o teste com link de campanha.
Mudança de produção no domínio inteiro: exige decisão do dono.

## Correção aplicada — 17/09/2026 13:19 UTC

Autorizada pelo dono após confirmar que as páginas WordPress legadas não perdem nada.
Única linha alterada em `/public_html/.htaccess`: `frame-src` passou a incluir
`https://www.facebook.com`; `frame-ancestors`, `X-Frame-Options` e `clkdmg.site` mantidos.
Backup: `.build/htaccess-backup/20260917T131927Z/before.htaccess` (arquivo remoto conferido
igual a `after.htaccess`). Reverter: reenviar `before.htaccess` e limpar cache.
Cache Cloudflare limpo nas 8 slugs e variações de campanha.

Reteste (envios abortados no navegador de teste): DRB, BCE, BPV, MPG, MCE, COE, GDP e
ECM-26 enviam 1 PageView por pixel com URL limpa (GET) e com link de campanha (POST),
zero bloqueios. Raiz WordPress carrega sem erros. Risco: o plugin `http-headers`
reescreve o bloco se alguém salvar as configurações dele no painel do WordPress.

## ECM-26 publicada — 17/09/2026

`./publicar.sh --build .build/ecm-26 ecm-26`, cache limpo. HTML público igual ao build salvo
beacon e ofuscação de e-mail do Cloudflare. Preço local não commitado (R$ 547) já estava no ar
e foi preservado. No ar: biblioteca Meta em 0,3–0,6s, GTM 5,2s parado / 2,2s com rolagem,
1 PageView por pixel com URL limpa e de campanha, sem duplicidade nem erros JS.
