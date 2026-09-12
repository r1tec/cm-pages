# BPV — migração do Lovable para cm-pages

**Estado: plano, sem execução da migração.** Pedido de 12/09/2026: trazer a BPV
de `https://pv.contemmagia.com.br/bpv` para `https://contemmagia.com.br/bpv`,
otimizar, instalar seu chat e redirecionar o endereço antigo; retirar a BPV do
Lovable somente depois da entrega. O pedido mais recente delimita esta etapa
à investigação e ao plano. Nenhuma BPV, regra de redirecionamento ou DNS foi alterada.

## Diagnóstico confirmado

Inspeção pública em Chrome, 390/1440 px, e PageSpeed em 12/09/2026:

| Métrica | Celular | Desktop |
| --- | --- | --- |
| PageSpeed | 77 | 93 |
| Primeira pintura (FCP) | 1,5 s | 0,2 s |
| Conteúdo principal (LCP) | 1,9 s | 0,7 s |
| Bloqueio de processamento (TBT) | 980 ms | 220 ms |
| Deslocamento visual (CLS) | 0,020 | 0,011 |

É uma amostra, não uma média de visitantes. A página **já tem otimizações**:
conteúdo presente no HTML recebido, imagens WebP e 34 de 35 imagens com
carregamento adiado. Portanto, não presumir uma aplicação React vazia nem
reconstruir o visual do zero. O gargalo mais evidente é processamento JavaScript;
os audits também apontam fontes e código não utilizado. Investigar as contribuições
do bundle próprio e dos terceiros antes de atribuir todo o custo ao Lovable.

- Título: Guia de Benzimento dos Pretos Velhos | Escola Contém Magia.
- Oito links de compra para `https://pay.contemmagia.com.br/c/bpv`; a campanha
  de teste chegou aos oito links. Suporte em `https://wa.me/message/LOSG4ESEXJUJB1`.
- Quatro âncoras para exemplos de benzimento e quatro botões de depoimento.
- Nenhum formulário ou chat na página inicial observada.
- GTM `GTM-P629X98`, GA `G-CGY4CM7NXE`, Ads `AW-956533053`, Clarity
  `hvofrp21xv` e pixels Meta `197461362094441` / `884049927923756` observados.
- Na navegação de diagnóstico, GTM iniciou em 114 ms e a biblioteca Meta em
  430 ms. O carregamento atual é diferente do padrão novo de Meta independente
  e GTM por interação/5 s.
- Bundle próprio `assets/index-BDmEXcpx.js`: cerca de 106 KB transferidos nessa
  navegação; CSS `assets/bpv-CBn6JYGb.css`: cerca de 19 KB. Não são o tamanho
  total da página nem prova de que todo o bundle pode ser removido.
- Canonical atual aponta para `https://pv.contemmagia.com.br/bpv`.
- DNS público de `pv.contemmagia.com.br` retornou A `185.158.133.1`. A
  configuração administrativa de proxy, TLS e regras ainda precisa ser lida.

## Decisões propostas

1. Preservar integralmente conteúdo, aparência, preço, bônus, depoimentos e compra.
   Preferir obter o código original pelo projeto/repositório conectado ao Lovable.
   A captura pública serve de referência e recuperação; não substitui a fonte
   quando ela estiver disponível.
2. Produzir uma página estática em `bpv/`, com assets locais e JavaScript pequeno
   para as interações realmente existentes. O HTML público já vem preenchido;
   avaliar o que o bundle faz antes de removê-lo. A BPV não é uma exportação
   `__bundler/manifest` do Claude Design e não deve ser tratada como tal.
3. Usar o mesmo opt-in `rastreamento.json` para Meta antecipada, preservando os
   dois pixels e a prevenção da repetição inicial do GTM. Demais tags seguem
   interação/5 s; sem alterar consentimento ou acrescentar dados coletados.
4. Instalar exclusivamente o chat enviado pelo dono:
   `data-widget-id="6aa5bb4e8eb25ab4caf59f7c"`, loader
   `https://widgets.leadconnectorhq.com/loader.js`, resources URL
   `https://widgets.leadconnectorhq.com/chat-widget/loader.js`.
   Preservar essa resources URL, que difere da instalação antiga das outras
   páginas. Aparência e comportamento iguais à MCE: WhatsApp persistente,
   selo visual, animação discreta e download em 5/7/10 s.
5. Redirecionar somente a rota BPV, mantendo campanhas. Não redirecionar o
   subdomínio inteiro nem despublicar um projeto que ainda sirva outras páginas.

## Execução sequencial proposta

### Build 1 — fonte, inventário e referência preservada

- Localizar projeto Lovable e repositório conectado; exportar/sincronizar código
  quando necessário. Registrar versão e dependências, sem modificar a publicação.
- Inventariar todas as rotas servidas por `pv.contemmagia.com.br` e pelo projeto;
  identificar se existem outros consumidores antes de qualquer mudança no host.
- Preservar HTML, CSS, fontes, imagens, URLs dos vídeos e screenshots completos
  em celular/desktop. Conferir preço/copy e criar `bpv/REGRAS.md` com a fonte.
- Mapear os quatro depoimentos, âncoras, possíveis estados após rolagem e
  referências absolutas a `/assets/`; no novo destino serão assets de `/bpv/`.

**Aceite:** fonte e dependências recuperáveis, conteúdo inventariado e rollback
possível. Não pode alterar o endereço público nem interromper campanhas.

### Build 2 — versão local fiel e otimizada

- Importar para `bpv/index.html` e `bpv/assets/`. Reaproveitar HTML pronto e
  remover dependências de edição/hospedagem do Lovable apenas se dispensáveis.
- Preservar as funções do bundle necessário, ou substituí-las por JS leve com
  prova de equivalência. Manter vídeo sob demanda e imagens abaixo da dobra adiadas.
- Avaliar fontes locais, `font-display`, tamanhos responsivos, capa prioritária
  e custo de execução. Não recomprimir imagens às cegas nem remover rastreamento
  para melhorar a nota.
- Aplicar Meta antecipada e o chat próprio. Atualizar canonical, metadados e
  caminhos internos para o novo endereço. Checkout permanece em `/c/bpv`.
- Preparar via `python3 preparar.py bpv --saida /tmp/preview-bpv --conferir`.
  Usar o caminho de HTML estático do pipeline; verificar o resultado real.
- Testar em 390/1440 px: fidelidade, oito CTAs, UTM/fbclid/gclid sem perdas,
  âncoras, quatro depoimentos, chat aberto/fechado e falha do fornecedor.
  Um PageView inicial por pixel; outros eventos e visitas posteriores intactos.

**Aceite:** mesma página e mesma compra, sem dependência funcional do Lovable;
sem imagens quebradas, overflow ou regressão de interação. Meta inicia sem
esperar GTM; chat não usa o atendimento de outra página. Não enviar mensagens
ou realizar transações de teste.

### Build 3 — nova URL publicada e verificada

- Com execução/publicação autorizada para a BPV, enviar o build validado por
  `./publicar.sh --build /tmp/preview-bpv bpv` e limpar cache pelo pipeline.
- Confirmar HTTPS/HTTP 200 e versão entregue no novo endereço, com e sem campanha.
  Reusar testes da mesma versão e conferir particularidades do destino público.
- Medir PageSpeed móvel/desktop e comparar FCP/LCP/TBT/CLS à referência acima.
  Referência de 90+ orienta a otimização, sem promessa de nota constante. Examinar
  toda regressão concreta e comunicar limites em vez de declarar aprovação falsa.
- Antecipar Meta privilegia o início da coleta e tem custo: nas demais páginas
  desta sessão houve queda da nota móvel. Não prometer aumento de conversão ou
  recepção no painel Meta com base apenas em pedidos de rede do navegador.

**Aceite:** nova URL funcional e fiel, rastreamento validado, desempenho medido.
O endereço antigo ainda funciona no Lovable durante esta etapa.

### Build 4 — redirecionamento restrito e reversível

- Ler a configuração efetiva de DNS/TLS/Cloudflare e regras existentes. DNS
  sozinho não redireciona caminhos. Usar regra HTTP no edge, preferencialmente
  Cloudflare, se o host estiver sob proxy e a configuração permitir sem afetar
  outras rotas; caso contrário, definir a hospedagem do redirecionador primeiro.
- Expressão proposta: host `pv.contemmagia.com.br` e caminho exatamente `/bpv`
  ou `/bpv/`; destino `https://contemmagia.com.br/bpv/` (validar URL canônica
  efetiva). Preservar query string explicitamente.
- Começar com 302 para o teste de corte. Validar URLs limpas, UTMs, fbclid,
  gclid, barra final e âncoras no navegador; sem loops ou redirecionamento JS.
  Após estabilidade comprovada, trocar para 301. Evitar cadeias desnecessárias.
- Testar outras rotas do host e a raiz; somente BPV pode mudar. Arquivar a
  configuração anterior e o procedimento exato de rollback.

**Aceite:** um redirecionamento de BPV ao novo destino, parâmetros preservados,
HTTPS válido e nenhuma interferência nas demais rotas. Não remover DNS/TLS
do endereço antigo: anúncios e favoritos continuam precisando dele.

### Build 5 — retirar a BPV do Lovable

- Confirmar primeiro que o redirecionamento e os assets necessários funcionam
  independentemente da publicação antiga. Guardar fonte e versão anterior.
- Se o projeto contiver outras páginas, remover somente a rota BPV; não
  despublicar o projeto inteiro nem desconectar domínio compartilhado.
- Se for exclusivo da BPV, despublicar a implantação apenas depois da verificação
  do corte, mantendo o backup. Excluir o projeto não é necessário para migrar.
- Conferir novamente URL antiga → nova, imagens, compra e atendimento. Registrar
  publicação, configuração final e commit/push em `origin`.

**Aceite:** a entrega BPV não depende mais do Lovable; o endereço antigo continua
levando corretamente ao novo e a restauração permanece documentada.

## Dependências para iniciar a execução

- Localização/acesso ao projeto Lovable ou ao repositório da BPV.
- Leitura das rotas que compartilham `pv` e da configuração efetiva de DNS/TLS.
- Autorização de execução da migração: nesta sessão, o pedido foi criar o plano.
  Não é necessário repetir essas perguntas a cada build após o escopo autorizado.

## Evidências e referências

- [BPV atual](https://pv.contemmagia.com.br/bpv), inspecionada em Chrome.
- Coleta inicial: `/tmp/rollout-antes-bpv.json`; inventário
  `/tmp/bpv-inventory.json`; HTML `/tmp/bpv-original-response.html`;
  screenshots `/tmp/bpv-before-mobile.png` e `/tmp/bpv-before-desktop.png`.
- [Exportação/sincronização GitHub no Lovable](https://docs.lovable.dev/integrations/github).
- [Publicação e despublicação no Lovable](https://docs.lovable.dev/features/publish).
- [Cloudflare: preservação de query no redirect](https://developers.cloudflare.com/rules/url-forwarding/single-redirects/settings/).
- [Cloudflare: requisito de DNS sob proxy](https://developers.cloudflare.com/fundamentals/manage-domains/redirect-domain/).

Preparação segue `.claude/skills/preparar-pagina/SKILL.md`, otimização segue
`.claude/skills/otimizar/SKILL.md` e envio segue `.claude/skills/publicar/SKILL.md`.
