# Testes da preparação de eduparmeggiani.com

Data: 10/09/2026. **Migração aplicada e validada pelo DNS público.**

Commit de código `0c51ac5` enviado com sucesso para `origin/main` em `r1tec/cm-pages`, após autorização explícita do usuário. O bloqueio anterior da revisão automática foi resolvido por essa autorização. Os relatórios operacionais permanecem locais, fora do commit público.

## Validação após a troca feita pelo usuário

- Os dois servidores autoritativos e os resolvedores Google/Cloudflare confirmaram A `187.108.194.90` e CNAME `www` para `eduparmeggiani.com`.
- Dezesseis consultas públicas às oito páginas, com e sem `www`, retornaram 200 com validação TLS ativa, sem redirecionamento de domínio. Todas continham o GTM esperado, sem a espera de três segundos.
- Chrome isolado **sem substituição de DNS** confirmou IP `187.108.194.90` e carregou as oito páginas com todas as imagens, GTM e links de checkout preservando UTM. Nenhum estouro horizontal no viewport móvel. Relatório técnico local: `/private/tmp/cm-public-browser-results.json`.
- Os dez destinos antigos foram testados a partir de eduparmeggiani.com: todos chegaram ao WordPress técnico com status 200, exatamente um encaminhamento e UTM preservada. Arquivo inexistente dentro de página migrada permaneceu 404, sem encaminhamento indevido.
- Permanecem as limitações descritas abaixo: recebimento no painel Meta não comprovado, renovação automática SSL pendente e arquivos secundários já ausentes em ECM-26-v1. Não houve alteração de anúncio, orçamento ou configuração de Pixel dentro do GTM.

## Alterações aplicadas

- Alias `eduparmeggiani.com` na conta cPanel `contemmagia`, compartilhando `/home/contemmagia/public_html` e os mesmos arquivos publicados.
- Certificado Let's Encrypt instalado no site principal. Preserva os nove nomes do certificado anterior e acrescenta somente `eduparmeggiani.com` e `www.eduparmeggiani.com`. Vencimento: 09/12/2026. Sem wildcard novo; site separado de alunos preservado.
- Bloco `config/eduparmeggiani.htaccess` inserido antes das regras existentes. Nenhuma linha anterior foi removida. SHA256 do arquivo completo instalado: `1e4bfffb33892d075994ef7c56eb3ec684726de74d6b659d88d54e4359b9ac8f`.
- Nove TXT de validação criados no Cloudflare foram removidos depois da emissão. TXT preexistente preservado. Os dois TXT de validação do GHL permanecem temporariamente.
- Após a orientação do usuário para reproduzir o GTM do WordPress, o carregador foi igualado ao original: assíncrono e imediato. Sete HTMLs receberam apenas essa substituição; ECM-26-v1 já era igual. Publicação por `./publicar.sh --gtm-original --aplicar ...`, com backups e conferência de que o restante do HTML permaneceu byte a byte idêntico. Assets e alterações simultâneas do usuário em páginas locais foram preservados. Nenhum anúncio editado ou compra efetuada.

Backups privados, sem versionamento: `/private/tmp/cm-migration-backup/ssl-before.json` e `/private/tmp/cm-migration-backup/root.htaccess.before`. Certificado e chave novos em `/private/tmp/cm-migration-acme/config/live/cm-dominios/`. Não copiar chaves para documentos, Git ou mensagens.

## Resultados antes do DNS

Os testes HTTP usaram resolução local explícita para `187.108.194.90`, SNI correto e validação TLS ativa. O navegador isolado também resolveu apenas os dois nomes da migração para esse IP, sem editar o DNS público ou o arquivo hosts do sistema.

| Página | HTTPS/HTML em edu, www.edu e contemmagia | Imagens carregadas no navegador móvel | Parâmetros no checkout |
|---|---|---:|---|
| bce | 200; conteúdo idêntico | 6/6 | UTM e fbclid preservados |
| coe | 200; conteúdo idêntico | 16/16 | UTM e fbclid preservados |
| drb | 200; conteúdo idêntico | 1/1 | UTM e fbclid preservados |
| mce | 200; conteúdo idêntico | 3/3 | UTM e fbclid preservados |
| mpg | 200; conteúdo idêntico | 3/3 | UTM e fbclid preservados |
| gdp | 200; conteúdo idêntico | 7/7 | UTM e fbclid preservados |
| ecm-26 | 200; conteúdo idêntico | 15/15 | UTM e fbclid preservados |
| ecm-26-v1 | 200; conteúdo idêntico | 2/2 | UTM e fbclid preservados |

Viewport 390×844: nenhuma página apresentou largura excedente. As imagens abaixo da dobra foram carregadas explicitamente para distinguir carregamento adiado de arquivo quebrado. BCE também foi conferida visualmente por captura. Isso não é uma auditoria completa de todos os tamanhos de tela.

Os sete destinos de checkout abriram o produto correspondente e a seção de pagamento no navegador, sem preenchimento ou envio. As duas páginas ECM usam `/c/ecm-26`. Não houve pedido de teste, comprovação de Purchase, CAPI ou deduplicação.

| Regra | Resultado observado |
|---|---|
| `/` no domínio edu | 302 para raiz técnica do WordPress |
| `/iat/` com UTM/fbclid | 302 para mesma página técnica, parâmetros preservados |
| `/mpp` | 302 para `/mpp/` no WordPress técnico |
| `/bce` | 301 para `/bce/`, mantendo eduparmeggiani.com |
| Imagem inexistente em `/bce/assets/` | 404 sem redirecionamento |
| Caminho desconhecido | 404 sem entregar o WordPress de contemmagia |
| `/wp-login.php` em edu | 404; administração continua no endereço técnico |

Os dez destinos antigos (`/`, `/iat/`, `/mpp/`, `/t3x/`, `/wmpp-obrigado/`, `/bpa/`, `/bco/`, `/6-edb/`, `/6-edb-obrigado/`, `/drb-vsl/`) responderam 200 no endereço técnico com UTM, sem redirecionamentos HTTP adicionais. Formulários, login e transações antigas não foram exercitados.

## Limitações encontradas

1. **Recebimento no painel Meta não verificado.** O usuário confirmou que toda a instalação passa pelo GTM e orientou usar `https://crhishmxlb.wpdns.site/bce/` como referência. O container é `GTM-P629X98`; o carregamento agora é imediato como nessa referência, sem Pixels adicionais fora dele. Após a publicação, as oito páginas retornaram 200 e continham exatamente um carregador normalizado. Os Pixels `197461362094441` e `884049927923756` carregam pelo GTM. Em BCE no domínio contemmagia.com.br, ambos enviaram PageView com resposta HTTP 200. Em eduparmeggiani.com, o teste não observou esses pedidos, tanto no novo servidor quanto no WordPress público atual, inclusive depois de retirar o atraso. Isso não comprova perda geral das campanhas nem regressão causada pela migração. Não apresentar a preservação da instalação como prova de recebimento de conversões no painel Meta; não alterar tags ou consentimento por tentativa.
2. **Renovação SSL ainda não garantida.** A emissão manual não agenda renovação. O perfil WHM não permite consultar a configuração geral AutoSSL; a versão 110 não oferece a função de consulta de renovação tentada. Não desinstalar o certificado para forçar emissão. Confirmar com a hospedagem a renovação da conta após a troca do DNS, antes de 09/12/2026.
3. **Erros secundários existentes.** `/~flock.js` de ECM-26-v1 já retorna 404 em contemmagia.com.br e também retorna 404 em edu. O navegador também solicitou um favicon ausente na raiz. As imagens das páginas passaram. Esses scripts/ícones não foram alterados nesta tarefa.
4. **Diferença de cliente HTTP.** O servidor respondeu 403 a curl com identificação genérica e 200 com identificação completa de Chrome. Navegadores carregaram as páginas e imagens. Nenhuma proteção foi desativada; não atribuir indisponibilidade geral ao site com base no cliente bloqueado.

## Troca realizada pelo usuário no GHL

Aplicada pelo usuário e confirmada pelos testes públicos acima. A integração GTM foi igualada à referência indicada pelo usuário; não confundir essa validação com comprovação de recebimento no painel Meta.

| Tipo/nome | Valor anterior para recuperação | Valor novo |
|---|---|---|
| A — eduparmeggiani.com | 104.18.185.50 | 187.108.194.90 |
| CNAME — www | crhishmxlb.wpdns.site | eduparmeggiani.com |

Manter TTL Auto e demais registros. Não adicionar URL Redirect no GHL. Após a troca: conferir DNS autoritativo, Google e Cloudflare; abrir páginas publicamente sem resolução local; conferir HTTPS, parâmetros, checkout e rastreamento. Se ocorrer falha relevante nova, restaurar os dois valores anteriores e manter o novo servidor operacional durante a propagação.

## Texto preparado sobre renovação — não enviado

> Na conta cPanel `contemmagia`, instalamos um certificado Let's Encrypt manual com validade até 09/12/2026 para o site principal, preservando seus nove nomes anteriores e adicionando `eduparmeggiani.com` e `www.eduparmeggiani.com`. Precisamos garantir renovação automática após apontar esses dois nomes para `187.108.194.90`. Favor confirmar a cobertura e a elegibilidade no AutoSSL dessa conta, ou indicar a configuração suportada para renovação. Não remover o certificado válido, alterar outros sites nem reduzir os nomes já cobertos. O revendedor `poolocom` não consegue consultar `get_autossl_metadata` pela API.

## Resumo em linguagem simples

A mudança já está no ar: os links antigos dos anúncios abrem as oito páginas novas, com cadeado e sem mudar o domínio do visitante. As dez páginas antigas mapeadas encaminham para o WordPress. O GTM inicia como na referência original, e os Pixels continuam dentro dele. O recebimento no painel Meta não foi comprovado; a renovação do cadeado antes de 9 de dezembro ainda precisa ser garantida. Nenhum anúncio foi alterado.

## Publicações futuras

O publicador normal continua reconstruindo e verificando as páginas completas. `rastreamento.py` fornece o carregador único, utilizado tanto por `estatico.py` quanto pelo caminho estático de `otimizar.py`, evitando que uma fonte antiga restaure o atraso de três segundos.

O modo restrito `./publicar.sh --gtm-original <slugs>` prepara uma prévia com backup do HTML publicado; `--aplicar` envia somente a substituição do carregador conhecido, com comparação contra alterações simultâneas e limpeza do cache de HTML. Não muda imagens, estilos ou conteúdo e não envia o conteúdo local em edição. Backups desta execução: `.build/gtm-original-backup/20260910T141858519923Z`. Não usar esse modo para mudanças de design/conteúdo.

**Resumo final:** a migração está no ar e passou nos testes públicos de páginas, imagens, cadeado, GTM, links e encaminhamentos. O código foi enviado ao GitHub autorizado. A chegada dos eventos no painel Meta e a renovação automática do certificado ainda não foram comprovadas.
