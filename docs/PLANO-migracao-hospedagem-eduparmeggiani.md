# Migração de eduparmeggiani.com para a hospedagem nova

Data: 10/09/2026. Plano vigente, substitui `PLANO-migracao-dominios-campanhas-meta.md`.

## Estado atual — prevalece sobre o histórico de testes abaixo

- **Troca pública concluída pelo usuário e validada:** raiz A `187.108.194.90`, `www` CNAME `eduparmeggiani.com`, confirmados pelos dois DNS autoritativos, Google e Cloudflare. As oito páginas retornaram 200 com HTTPS tanto na raiz quanto em www; Chrome sem resolução forçada carregou todas as imagens e GTM das oito páginas. Os dez encaminhamentos antigos chegaram ao WordPress com 200, um único salto e parâmetros preservados. Código `0c51ac5` enviado ao GitHub após autorização explícita; relatórios operacionais mantidos locais. Restam a confirmação de recebimento no painel Meta e a renovação SSL, conforme `docs/TESTES-migracao-eduparmeggiani.md`.

- O usuário confirmou que `/bce/` abre em Wi-Fi, 5G, celular e computador.
- Nova rodada de testes: as oito páginas responderam **200 tanto pela Cloudflare quanto diretamente no IP da hospedagem**, com validação do certificado de `contemmagia.com.br`. Nenhuma regra de segurança foi alterada. A causa dos 403 anteriores não foi identificada; não afirmar indisponibilidade geral, dependência atual exclusiva de cache nem correção executada por nós.
- **Cadastro realizado:** `eduparmeggiani.com` foi adicionado como alias da conta `contemmagia`, reaproveitando `/home/contemmagia/public_html`. A consulta `DomainInfo/domains_data` confirmou o alias. O domínio semelhante `eduparmeggiani.com.br`, de outra conta no WHM, não foi alterado.
- **HTTPS instalado e conferido:** certificado Let's Encrypt com os nove nomes previamente protegidos e `eduparmeggiani.com`/`www.eduparmeggiani.com`, válido até 09/12/2026. Testes diretos ao IP com SNI validaram os quatro nomes principais e os serviços webmail/cPanel. Nenhum nome antigo perdeu cobertura; o site separado de alunos não foi alterado.
- Valores anteriores preservados para recuperação, se necessário: raiz `104.18.185.50`; `www` CNAME `crhishmxlb.wpdns.site`. A origem antiga permanece disponível no domínio técnico.
- **Regras instaladas:** bloco versionado em `config/eduparmeggiani.htaccess`, antes do WordPress existente e limitado aos dois hostnames de eduparmeggiani.com. 24 consultas às oito slugs em três hostnames retornaram 200 e HTML idêntico por slug. Raiz e páginas antigas testadas retornaram 302 preservando parâmetros; arquivos/rotas inexistentes retornaram 404; `/bce` normalizou para `/bce/` no mesmo domínio. O ajuste posterior de GTM está descrito abaixo.
- **Navegador validado:** oito páginas com todas as imagens carregadas, sem estouro horizontal em viewport 390×844. Teste com Chrome isolado e resolução local do domínio antigo para o novo IP, sem editar DNS público. UTM e fbclid de teste preservados nos links de checkout. Dois 404 secundários observados: favicon automático na raiz e `/~flock.js` de ECM-26-v1 (este último também já faltava no domínio novo). Relatório privado: `/private/tmp/cm-origin-browser-results.json`. Requisições curl com User-Agent genérico continuaram recebendo 403; com identificação completa de navegador receberam 200. Não desativamos proteção.
- Orca voltou a funcionar no navegador externo Chrome; o erro de conexão ocorria no ambiente restrito. O usuário prefere executar pessoalmente a troca final no GHL, recebendo os valores após os testes.
- A emissão wildcard foi rejeitada pela revisão automática e abandonada. A alternativa restrita, com nomes exatos, foi autorizada, emitida e instalada. Os nove TXT temporários criados no Cloudflare já foram removidos por correspondência de nome e conteúdo; o TXT preexistente foi preservado. Os dois TXT temporários do GHL ainda podem ser removidos após a conclusão.
- O domínio permanece como alias: a tentativa de domínio adicional falhou pelo limite zero da conta, e o alias foi restaurado. Nenhuma quota foi alterada. `alunos.contemmagia.com.br` é outro site SSL e não deve ser modificado.
- Backup privado do SSL anterior e do `.htaccess` raiz em `/private/tmp/cm-migration-backup` (permissões restritas; não versionar). O certificado instalado, de onze nomes exatos, está em `/private/tmp/cm-migration-acme/config/live/cm-dominios`, vence em 09/12/2026 e não possui renovação automática por esse Certbot manual. Não declarar renovação resolvida: consultas WHM de configuração AutoSSL foram negadas pelo perfil remoto.
- Token Cloudflare liberado pelo usuário para DNS na zona de `contemmagia.com.br`; criação e remoção dos TXT foram concluídas por API. Nenhum A/CNAME do Cloudflare foi alterado.
- **GTM igualado à referência do usuário:** mesmo container `GTM-P629X98`, agora assíncrono e imediato como no WordPress técnico. Foi removida a espera artificial de três segundos de sete páginas; a oitava já usava esse carregamento. Ajuste publicado pelo modo restrito do publicador, preservando byte a byte o restante dos HTMLs e todas as alterações locais paralelas. As oito páginas foram reconferidas com 200 e exatamente um carregador GTM. Os Pixels continuam somente dentro do GTM. **Não foi verificada a chegada no painel Meta:** PageView foi observado em contemmagia, mas não nos testes de edu, tanto na origem nova quanto no WordPress atual. Relatório atualizado em `docs/TESTES-migracao-eduparmeggiani.md`.
- O texto de suporte no fim é apenas histórico/preparação, não deve ser enviado como denúncia de indisponibilidade geral atual.

## Objetivo e autorização

Receber `eduparmeggiani.com` e `www.eduparmeggiani.com` na hospedagem das páginas novas, mantendo as URLs das campanhas Meta. Servir as oito páginas migradas nesse endereço e em `contemmagia.com.br`. Encaminhar por redirecionamento temporário 302 as páginas antigas explicitamente identificadas para `https://crhishmxlb.wpdns.site/<caminho>`.

O usuário informou que as páginas não migradas não têm campanha ativa e aceita indisponibilidade temporária dessas páginas. Isso não autoriza indisponibilidade das páginas de campanha, retirada do WordPress, alteração dos anúncios, compras reais ou mudança de serviços de email.

O pedido atual autoriza refazer o plano, testar e executar a migração completa, inclusive publicação e operação pelos painéis do navegador Orca. Não pedir novamente aprovação rotineira das etapas. Falta de acesso ou de prova necessária deve ser reportada; não mudar o DNS para contornar uma falha ainda aberta.

## Arquitetura

| Entrada | Comportamento desejado |
|---|---|
| `eduparmeggiani.com/<slug-migrada>` | Página estática nova, sem mudança de domínio no navegador |
| `www.eduparmeggiani.com/<slug-migrada>` | Página nova ou normalização para o domínio sem www, preservando caminho e parâmetros |
| `contemmagia.com.br/<slug-migrada>` | Página nova, como atualmente |
| `eduparmeggiani.com/<pagina-antiga-confirmada>` | 302 para o endereço técnico do WordPress com caminho e parâmetros preservados |
| Arquivo inexistente dentro de página migrada | 404 real; nunca redirecionar imagem, CSS ou script para o WordPress |
| Raiz, administração, APIs e formulários antigos | Mapear separadamente; não encaminhar POST por 302 sem verificar o fluxo |

As oito slugs locais são `bce`, `coe`, `drb`, `ecm-26`, `ecm-26-v1`, `gdp`, `mce`, `mpg`. Confirmar URLs reais dos anúncios e seus aliases antes da troca.

O domínio permanece registrado e com DNS administrado no GHL. A nova estratégia não depende de instalar um Worker na Cloudflare administrada pelo GHL nem de transferir o registro do domínio.

Adicionar o domínio à conta correta no WHM/cPanel com HTTPS e destino de arquivos explícito. O DNS aponta para o servidor validado, não para um IP de borda da Cloudflare copiado de uma consulta pública. Confirmar o tratamento de proxy/SSL do GHL para o novo destino.

A hospedagem de `contemmagia.com.br` também contém um WordPress em `public_html`. Não compartilhar a pasta raiz sem conferir as regras: isso poderia entregar o WordPress errado ou redirecionar para o domínio novo. Escolher no painel uma configuração que sirva as páginas migradas e isole por hostname as regras do domínio antigo. Preferir reaproveitar os artefatos publicados sem manter cópias manuais concorrentes. Ajustar o publicador canônico caso seja necessário um destino adicional.

O retorno ao WordPress deve usar lista explícita de páginas. Revisar links absolutos, mídia, formulários e eventuais redirects de volta ao domínio antigo. O WordPress usa os endereços configurados para gerar suas URLs; uma resposta 200 isolada não comprova o fluxo inteiro. [WordPress: migração e endereços](https://developer.wordpress.org/advanced-administration/upgrade/migrating/).

## Testes já executados

Todos os testes abaixo foram de leitura. Nenhum domínio foi adicionado, nenhum DNS foi alterado e nenhum cache foi limpo nesta etapa.

| Teste | Resultado | Consequência |
|---|---|---|
| FTP com TLS usando configuração local | Login e listagem bem-sucedidos | Acesso aos arquivos disponível |
| Arquivos em `/public_html/bce` e `/public_html/coe` | `index.html`, assets e `.htaccess` presentes; HTML 0644 e diretórios 0755 nos itens conferidos | Ausência de arquivos e permissões básicas desses itens não explicam o bloqueio |
| `.htaccess` dessas duas páginas | Regras equivalentes de compressão/cache | Não foi encontrado bloqueio explícito nesses arquivos |
| `.htaccess` da raiz | Contém WordPress e regras de outro site | Reutilização da raiz exige isolamento por domínio |
| Oito slugs no domínio novo | `coe` e `ecm-26` responderam 200 em URLs já armazenadas; seis responderam 403 | Não pronto para campanhas |
| Consulta direta ao IP FTP `187.108.194.90` com Host/SNI `contemmagia.com.br` | Oito slugs responderam 403; certificado validado pelo cliente | Conferir virtual host, logs e segurança da hospedagem; ainda confirmar se esse é o destino configurado na Cloudflare |
| HTML explícito em `bce`, `coe`, `ecm-26` pela Cloudflare | 403 e `CF-Cache-Status: BYPASS` | Não é somente ausência de DirectoryIndex |
| `coe/` com parâmetro de teste | 200 e `CF-Cache-Status: HIT` | Uma cópia em cache pode mascarar falha da origem; não purgar antes de corrigir |
| Endereço técnico WordPress, com User-Agent de navegador | `bce`, `drb`, `mce`, `mpg`, `gdp`: 200, domínio técnico preservado | Caminho de retorno plausível; ainda testar páginas realmente não migradas |
| Endereço técnico WordPress | `coe`, `ecm-26`, `ecm-26-v1`: 404 | Não usar essas URLs como recuperação automática |
| Consultas WordPress sem User-Agent de navegador | 403 nos cinco caminhos inicialmente testados | Conferir regras de segurança e acesso dos revisores/rastreadores; não presumir que todos os clientes recebem 200 |
| Token Cloudflare local, teste anterior | Ativo, leitura da zona `contemmagia.com.br`; DNS retornou 403 | Falta leitura DNS para confirmar origem pelo painel/API |
| Orca CLI | `tab list`: `runtime_unavailable`; tentativa `open`: `runtime_open_timeout`; nova consulta sem conexão | Operação do navegador depende de restabelecer a conexão com o aplicativo |
| Token WHM fornecido pelo usuário | Validado em `br.midgard4010.com.br:2087`, usuário `poolocom`; consultas `version`, `listaccts` e cPanel via WHM funcionaram | Acesso de gestão confirmado para prosseguir nas operações permitidas |
| Conta WHM/cPanel | `contemmagia`, proprietário `poolocom`, não suspensa; IP `187.108.194.90`, document root `/home/contemmagia/public_html`; domínio antigo ausente | Configuração corresponde ao FTP; nenhum domínio foi adicionado ainda |
| Consulta ampliada de erros | 300 registros: predominam tentativas de servir `403.shtml` inexistente; sem causa original nos registros disponíveis | Não criar página de erro como suposta correção do bloqueio |
| Regras adicionais | Proteção de hotlink desativada, lista de handlers vazia; diretório pessoal 0711, `public_html` 0750/grupo 65534, assets conferidos 0644 | Nenhum bloqueio comprovado nesses itens; não alterar permissões por tentativa |
| Diagnóstico de firewall | cPanel `ModSecurity/list_domains`: recurso indisponível; WHM `modsec_get_log`: permissão negada | Os acessos atuais não permitem concluir diagnóstico do firewall; isso não comprova que ele seja a causa |
| Chrome isolado | Tentativa headless terminou em timeout | Não conta como validação de navegador; Orca continua indisponível |

Tempos de uma consulta HTTP isolada não são medição de desempenho da página. Ainda não houve validação visual no navegador, teste de eventos no painel da Meta nem pedido de teste no checkout.

O sitemap público do WordPress retornou 15 páginas, sendo dez fora das oito slugs migradas: `/`, `/iat/`, `/mpp/`, `/t3x/`, `/wmpp-obrigado/`, `/bpa/`, `/bco/`, `/6-edb/`, `/6-edb-obrigado/`, `/drb-vsl/`. É um inventário inicial, não prova de completude. A raiz, `/iat/` e `/mpp/` foram testadas no domínio técnico com `utm_source=cm_migration_test`: responderam 200, mantiveram o domínio técnico e o parâmetro, sem ciclo HTTP observado. Conteúdo, links e eventos dessas páginas ainda não foram validados no navegador.

## Etapas e critérios de aceite

### 1. Acessos, inventário e recuperação da origem

Confirmar URL e usuário WHM, testar token com operação de consulta restrita, identificar conta/domínio/document root e consultar os logs relacionados aos 403. Conferir Cloudflare sem limpar o cache que hoje sustenta respostas 200. Corrigir a causa comprovada, preservando regras e sites alheios.

Inventariar páginas antigas via sitemap/WordPress, raiz, links, mídia, formulários e endereços dos anúncios. Salvar configurações de domínio/DNS/SSL e arquivos afetados antes de alterações.

**Tem que fazer:** origem saudável, oito páginas com 200 e arquivos funcionando, acesso de gestão confirmado, inventário de destinos e provas salvos sem credenciais.

**Não pode acontecer:** purgar o cache com origem bloqueada, desativar proteção global sem diagnóstico, alterar outros domínios ou assumir que sitemap contém todos os links de campanhas.

### 2. Preparar o domínio na hospedagem e o retorno das páginas antigas

Adicionar domínio sem alterar o DNS público. Definir document root e regras por hostname. Configurar os 302 por página, respeitando query string, codificação e barras. Validar HTTPS para os dois hostnames antes da troca; se a emissão depender de DNS, usar validação DNS quando disponível e preparar a emissão sem interromper visitantes. Não tratar certificado do domínio novo como válido para o antigo.

Publicação de páginas exclusivamente por `./publicar.sh [slug ...]`, com as verificações canônicas. Configuração de virtual host, domínio e SSL ocorre pelo painel/API, não por outro publicador de páginas. Nenhuma criação de cópias manuais da mesma página.

**Tem que fazer:** respostas corretas ao Host/SNI do domínio antigo em testes antes da troca, certificado válido e regras de retorno ensaiadas.

**Não pode acontecer:** trocar endereço da campanha no navegador nas páginas migradas, servir WordPress da conta errada, ciclo de redirects, tratar arquivos faltantes como páginas antigas.

### 3. Validar páginas, parâmetros e rastreamento

Testar as oito páginas no celular e desktop, caminhos com e sem barra, www, parâmetros UTM/fbclid e parâmetros próprios de checkout. Conferir os links de produto, oferta, cupom, dados dinâmicos e ausência de erros de assets/JavaScript.

Conferir Pixel/dataset atual, GTM, consentimento, gatilhos por hostname e eventos reais esperados. Validar o fluxo até compra em modo de teste do checkout e a deduplicação Pixel/CAPI quando existente. Nenhuma compra real. Testes do navegador não substituem a chegada do evento ao Gerenciador de Eventos.

Testar páginas não migradas e links que saem delas para as migradas. Formulários e autenticação exigem tratamento próprio; um 302 pode mudar o método e perder dados.

Medir velocidade em condições equivalentes, com cache frio e aquecido. Definir limites de regressão após obter a linha de base; não prometer nota ou estabilidade comercial sem medição.

**Tem que fazer:** página correta e rastreamento preservado no domínio usado pelas campanhas; relatório por rota e lista explícita de limitações.

**Não pode acontecer:** evento de compra disparado no clique, duplicação/perda de eventos, tags removidas para melhorar pontuação, redirecionamento de parâmetros de oferta para produto incorreto.

### 4. Trocar DNS no GHL e validar imediatamente

Salvar o conjunto completo de registros atuais. O print confirma A do domínio raiz `104.18.185.50` e CNAME `www` para `crhishmxlb.wpdns.site`; reler no momento da troca e preservar TTL/proxy, MX/TXT e demais serviços que existirem.

Atualizar somente raiz e www para o destino validado da hospedagem. O domínio inteiro muda nesta estratégia; manter a origem antiga disponível durante propagação. Não mudar nameservers ou transferir registro.

Testar resolução por mais de um resolvedor, HTTPS, oito páginas, parâmetros, checkout e retorno das páginas antigas após a troca. Acompanhar erros e eventos imediatamente e nas primeiras horas. Comparar desempenho agregado em 24–72 horas conforme volume; isso é acompanhamento, não prova automática de estabilidade de CPA/ROAS.

**Tem que fazer:** todas as páginas com campanhas chegam à versão nova correta, inclusive www, com eventos funcionando.

**Não pode acontecer:** corte com 403 ainda aberto, dependência de cache antigo para aparentar sucesso ou alteração de anúncio/orçamento.

### 5. Entrega e retorno seguro

Entregar mapa final, configurações aplicadas, provas dos testes e rotina de publicação/cache. GitHub permanece espelho: commit/push apenas dos arquivos desta tarefa, preservando alterações locais alheias.

Se houver falha relevante de página de campanha, SSL, checkout ou eventos, restaurar os registros anteriores e validar a recuperação. Retorno DNS não é instantâneo: alguns visitantes continuam no servidor novo durante o cache dos resolvedores. Manter o destino novo em estado seguro e o WordPress ativo. Para páginas sem equivalente antigo, preparar versão estática saudável anterior.

**Tem que fazer:** procedimento de retorno preparado antes do corte e WordPress mantido durante estabilização.

**Não pode acontecer:** apagar a origem antiga, declarar entrega completa sem os testes pendentes ou esconder bloqueios de acesso.

## Acessos restantes para concluir

| Serviço | Situação / o que falta |
|---|---|
| FTP da hospedagem | Validado por TLS; não pedir senha novamente |
| WHM/cPanel | Autenticação validada. Diagnóstico do firewall está fora das permissões atuais; precisa de acesso restrito aos registros pertinentes ou análise do provedor |
| Cloudflare de contemmagia.com.br | API DNS liberada e utilizada com sucesso; validações temporárias concluídas e limpas |
| GHL | Usuário prefere orientação, mas também autorizou navegador Orca. Precisará de sessão autenticada acessível para executar a troca; caso indisponível, fornecer os valores exatos para o usuário aplicar |
| Orca | Conexão disponível; navegador externo e navegador de testes operacionais |
| Meta/GTM/checkout | Ainda não há acesso validado aos eventos, configuração de tags e pedido de teste. Necessário para afirmar rastreamento verificado de ponta a ponta |

Não há necessidade de extrair as credenciais GHL do Supabase enquanto o fluxo for pelo painel autenticado. O token WHM não foi colocado em documento, Git ou logs de testes.

Referências técnicas: [autenticação WHM por token](https://api.docs.cpanel.net/guides/guide-to-api-authentication/guide-to-api-authentication-api-tokens-in-whm), [gerência de domínios no cPanel](https://docs.cpanel.net/cpanel/domains/domains/manage-the-domain/).

## Resumo em linguagem simples

**Vamos fazer o domínio dos anúncios abrir as páginas novas diretamente na hospedagem nova.** O visitante continua vendo `eduparmeggiani.com`. As páginas antigas terão encaminhamentos específicos para o WordPress enquanto terminamos a migração delas.

1. Conferir a hospedagem: na rodada mais recente, as oito páginas abriram corretamente também nos testes diretos ao servidor.
2. Cadastrar o domínio nessa hospedagem, preparar o cadeado HTTPS e os encaminhamentos das páginas antigas.
3. Testar as páginas e o caminho até a compra, incluindo o que a Meta recebe.
4. Só então trocar os dois apontamentos no GHL e conferir o resultado no endereço real.
5. Manter o WordPress e uma forma de voltar atrás até a mudança estabilizar.

O domínio, o HTTPS e os encaminhamentos estão preparados. As páginas e imagens passaram nos testes. Falta concluir a conferência do rastreamento antes da troca do DNS pelo usuário. A renovação automática do certificado ainda depende de confirmação na hospedagem.

### Informação para o suporte da hospedagem, se necessário

Texto preparado, não enviado:

> Na conta `contemmagia`, domínio `contemmagia.com.br`, requisições HTTPS para `/bce/index.html`, `/coe/index.html` e outras páginas estáticas retornam 403. Os arquivos existem, têm permissão 0644 e as pastas das páginas 0755. A conta não está suspensa, o document root é `/home/contemmagia/public_html`, hotlink protection está desativado e não há bloqueio explícito nos `.htaccess` conferidos. O problema também foi reproduzido diretamente em `187.108.194.90` com Host/SNI correto e certificado validado. Algumas URLs pela Cloudflare ainda respondem 200 com cache HIT; URLs sem cache retornam 403/BYPASS. O log disponível na conta registra principalmente a ausência de `403.shtml`, sem informar a causa original. Favor identificar a regra ou restrição exata no LiteSpeed/ModSecurity/Imunify e informar a correção específica. O revendedor `poolocom` recebe permissão negada ao consultar `modsec_get_log`. Não limpar o cache nem desativar globalmente a proteção para investigar.

O usuário confirmou que `/bce/` abre no próprio navegador/celular em Wi-Fi e 5G. Depois dessa confirmação, os testes automatizados também passaram nas oito páginas, inclusive diretamente na origem. A causa da mudança de comportamento permanece desconhecida.

## Resumo final em linguagem simples

A mudança já está no ar: os mesmos links dos anúncios abrem as oito páginas novas com cadeado HTTPS. As dez páginas antigas mapeadas encaminham para o WordPress. Os testes públicos confirmaram páginas, imagens, GTM, links de compra e encaminhamentos. O GTM inicia como na página original indicada pelo usuário; os Pixels permanecem dentro dele. O código foi enviado ao GitHub, sem os relatórios internos. Não foi comprovado o recebimento dos eventos no painel Meta. A renovação do cadeado antes de 9 de dezembro ainda precisa ficar garantida.
