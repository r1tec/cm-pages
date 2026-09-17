# WordPress do GHL para hospedagem própria

Data: 10/09/2026. Estado: levantamento concluído; viabilidade técnica condicionada aos acessos, capacidade e teste de restauração. Pedido desta sessão: investigar e planejar, sem instalar, publicar, mudar DNS ou cancelar serviços.

## Conclusão

É tecnicamente viável clonar o WordPress de `crhishmxlb.wpdns.site` para a hospedagem própria e servi-lo em `eduparmeggiani.com`, preservando conteúdo, edição e aparência. O caminho é um backup completo de arquivos e banco de dados, seguido de restauração isolada e adaptação dos endereços. A igualdade visual e funcional precisa ser comprovada: não significa copiar configurações específicas do servidor antigo sem ajustes.

O GHL documenta SSH com WP-CLI. A estratégia preferida combina APIs de administração com SSH/SFTP e WP-CLI; estes últimos são protocolos/ferramentas de terminal, não uma API HTTP. Não há necessidade de navegar página por página para migrar. Não foi encontrado, nas fontes consultadas, endpoint público documentado do GHL para exportação integral do WordPress; não prometer operação 100% REST. [SSH no GHL](https://help.gohighlevel.com/support/solutions/articles/155000005588-ssh-access-for-wordpress).

A economia ainda não foi quantificada: depende da cobrança específica de WordPress, licenças próprias necessárias, capacidade adicional e custo de backups/manutenção. Migrar WordPress não transfere automaticamente os funis nativos, contatos, automações, calendários ou outros serviços do GHL.

## Evidências e limites

Consultas públicas nesta sessão, sem autenticação e sem navegador:

| Verificação | Resultado |
|---|---|
| Origem `/` | HTTP 200, título Contém Magia |
| Origem `/wp-json/` | HTTP 200; home e URL no domínio técnico; namespaces Elementor, Elementor Pro, Hello Elementor, LiteSpeed e Akismet |
| API de páginas, até 100 itens | 14 páginas publicadas, uma página de resultados |
| API de posts | Um post publicado, `hello-world` |
| `/wp-sitemap.xml` | Índices de páginas, posts, categorias e usuários |
| Destino `/` | Segue encaminhamento para a origem técnica e chega com 200 |
| Destino `/bce/` | 403 com User-Agent simplificado; 200 com identificação completa de Chrome, comportamento já registrado anteriormente |

Inventário público: `drb-vsl`, `6-edb-obrigado`, `6-edb`, `bco`, `bce`, `mce`, `mpg`, `gdp`, `drb`, `bpa`, `wmpp-obrigado`, `t3x`, `mpp`, `iat`. Fontes: [páginas](https://crhishmxlb.wpdns.site/wp-json/wp/v2/pages?per_page=100&_fields=id,slug,link), [posts](https://crhishmxlb.wpdns.site/wp-json/wp/v2/posts?per_page=100&_fields=id,slug,link), [API](https://crhishmxlb.wpdns.site/wp-json/).

Isso não é o inventário completo: rascunhos, páginas privadas, templates, revisões, usuários, arquivos, tabelas de plugins e outras instalações exigem acesso administrativo. A presença dos namespaces não comprova versão, validade ou titularidade das licenças. Não foi confirmado se existe Multisite ou outro WordPress na assinatura; cada instalação adicional precisa de inventário e backup próprios.

Registros locais da migração anterior, não revalidados por API administrativa nesta sessão:

- `eduparmeggiani.com` é alias de `contemmagia.com.br` na conta `contemmagia`, ambos em `/home/contemmagia/public_html`, onde já existe um WordPress diferente.
- A tentativa anterior de criar domínio adicional falhou por limite zero. O domínio voltou a ser alias; não presumir que a quota mudou.
- As oito rotas novas são `bce`, `coe`, `drb`, `mce`, `mpg`, `gdp`, `ecm-26` e `ecm-26-v1`. O arquivo `config/eduparmeggiani.htaccess` mantém essas rotas, encaminha raiz e nove rotas antigas ao GHL e bloqueia as demais, inclusive administração.
- HTTPS instalado até 09/12/2026; renovação automática ainda pendente. Recebimento dos eventos no painel Meta também não foi comprovado.
- Há configuração FTP e Cloudflare no `.env`. O token WHM foi validado na sessão anterior, mas não consta das chaves desse arquivo; sua disponibilidade atual precisa ser confirmada por meio seguro. Nenhuma credencial foi exibida.

Referências locais: `docs/PLANO-migracao-hospedagem-eduparmeggiani.md` e `docs/TESTES-migracao-eduparmeggiani.md`. Autorizações históricas desses documentos não ampliam o pedido atual.

## Requisitos antes de executar

| Requisito | Como confirmar / situação |
|---|---|
| SSH da origem | Host, porta, usuário e autenticação na seção Sites → WordPress → Advanced Settings → FTP/SSH Access. Confirmar conexão e WP-CLI. Não presumir que SFTP concede shell. |
| Administração WordPress | Acesso próprio independente do login automático do GHL; inventário de plugins, temas, versões, licenças e conteúdo privado. Application Password pode ajudar na REST API, mas não substitui backup. |
| Arquivos e banco completos | Confirmar leitura dos arquivos e exportação de todas as tabelas pertinentes; medir tamanho, quantidade de arquivos e motores das tabelas para backup consistente. |
| Administração do destino | Revalidar token WHM/cPanel com consultas; confirmar permissões para banco, usuário, domínio, PHP e SSL. Preferir token restrito e SSH no destino. FTP sozinho não cobre toda a restauração. |
| Capacidade | Consultar disco livre, inodes, RAM, CPU, processos PHP, limites de banco, upload e tempo. Dimensionar produção, cópia de teste e backups coexistentes com folga; tamanho ainda desconhecido. |
| Compatibilidade | Levantar versões atuais antes de mudar. Referência atual do WordPress: PHP 8.3+, MariaDB 10.11+ ou MySQL 8.0+, HTTPS; compatibilidade dos plugins é um teste separado. |
| Isolamento | Document root e banco exclusivos. Confirmar possibilidade de domínio adicional ou conta dedicada e eventual preço antes de contratar. |
| Integrações | Mapear formulário, SMTP, vídeos, checkout, webhooks, tarefas agendadas, GTM/Meta, cookies e recursos hospedados fora do WordPress. Identificar quais dependem da assinatura a cancelar. |
| Licenças e cobrança | Titular do Elementor Pro e outros plugins pagos, direito de uso fora do GHL, valor efetivamente removível da mensalidade, custo do destino e de backup. |
| Operação contínua | Backup externo privado, restauração testada, atualização e responsável; renovação automática de HTTPS comprovada. |

Fontes: [requisitos do WordPress](https://wordpress.org/about/requirements/), [REST API](https://developer.wordpress.org/rest-api/reference/), [migração](https://developer.wordpress.org/advanced-administration/upgrade/migrating/), [domínios via cPanel](https://api.docs.cpanel.net/specifications/cpanel.openapi/domain-information/domaininfo-list_domains).

Não enviar senhas no documento ou no chat. Reaproveitar acesso seguro já disponível; se ausente, provisionar credenciais no armazenamento privado usado pela operação.

## Arquitetura proposta e decisão de conteúdo

**Preferência: instalação independente com pasta e banco próprios**, na mesma hospedagem se houver capacidade. Separar o domínio hoje cadastrado como alias exige uma troca controlada do cadastro, preservando SSL e rotas. Não extrair um backup por cima de `public_html`: isso poderia substituir o WordPress de Contém Magia e as páginas novas.

Primeiro preparar cópia de teste protegida contra acesso público e indexação, com emails, webhooks, pagamentos e tarefas automáticas impedidos de disparar para produção. Testar integrações apenas com destinos de teste. Ao entrar no ar, reativar somente o necessário e garantir que apenas uma instalação execute tarefas produtivas.

Se o plano não permitir raiz separada sem custo adicional, avaliar instalação em subpasta isolada com roteamento por hostname como alternativa. Essa opção requer ensaio específico de login, REST, uploads, links permanentes, regras do servidor e isolamento do outro WordPress; não é a escolha automática.

Decisão confirmada pelo usuário nesta sessão: **manter públicas as oito páginas novas**. Clonar também as versões antigas que existem no WordPress, mas sem fazê-las substituir as novas nas URLs coincidentes. As demais páginas e a raiz passam ao WordPress restaurado. A política de precedência deve cobrir também sitemap e URLs canônicas, para não anunciar versões conflitantes.

COE e as duas ECM não apareceram no inventário público da origem e continuam atendidas pelas versões novas. Nenhuma das oito rotas será substituída pela restauração.

O publicador atual continua sendo o único caminho para publicar páginas deste repositório. A futura execução deve definir como manter as oito rotas atualizadas no destino separado sem criar cópias manuais divergentes. Restauração de WordPress é operação de infraestrutura distinta; não executar o publicador sobre o backup nem usar a restauração para contornar as regras de publicação.

## Plano de execução

### 1. Confirmar acessos, conteúdo, capacidade e economia

Inventariar por WP-CLI e APIs: instalações, Multisite, tabelas, uploads, temas filhos, plugins comuns e obrigatórios, configurações, tarefas e integrações. Revalidar domínio/pasta do destino e resolver a quota que impediu separação. Confirmar política das oito rotas e valores de cobrança.

**Tem que fazer:** inventário privado completo, caminho de exportação/importação comprovado, arquitetura e custo conhecidos.

**Não pode acontecer:** considerar 14 páginas como todo o acervo, contratar algo sem autorização ou modificar o site em produção durante o levantamento.

### 2. Fazer e testar backup completo

Exportar o banco via WP-CLI/cliente de banco e copiar arquivos por SSH/SFTP. Incluir uploads, temas, plugins, mu-plugins, arquivos ocultos e configurações necessárias. Guardar versão original protegida; adaptar configurações específicas de hospedagem somente na cópia. Um XML de conteúdo, HTML baixado ou snapshot interno do GHL não substitui esse pacote portátil. Também guardar estado anterior do destino, regras de rotas, SSL e bancos afetados.

Produzir inventário de arquivos e hashes, verificar extração e importar o banco em ambiente isolado. Guardar cópia fora dos dois servidores, com acesso restrito; backups SQL nunca devem ficar disponíveis por URL pública.

**Tem que fazer:** restauração utilizável e comparação de tabelas/contagens, arquivos e hashes com o inventário.

**Não pode acontecer:** backup incompleto, arquivo público contendo dados ou chaves, sobrescrita de banco existente ou considerar o botão de download como prova de recuperação.

### 3. Restaurar e validar na hospedagem

Criar banco/usuário exclusivos e restaurar a cópia protegida. Ajustar URLs com ferramenta que preserve dados serializados, simular substituições antes de aplicar e limitar ao banco da instalação. Revisar dados e arquivos gerados pelo Elementor, regenerar CSS/cache e conferir licença no novo endereço. Adaptar plugins específicos da hospedagem antiga após identificar sua função.

Comparar conteúdo privado por contagens e amostragem; verificar todas as rotas públicas inventariadas por HTTP. Fazer verificação visual automatizada pontual em celular e desktop, incluindo popups e formulários. Usar navegador apenas onde a renderização/interação é necessária; HTTP 200 sozinho não comprova aparência. Testar login, editor, REST, mídia, redirecionamentos, checkout em modo de teste, UTM/fbclid e eventos em ferramenta de teste correspondente, sem compra real.

**Tem que fazer:** visual e funções essenciais equivalentes; nenhuma dependência indispensável do domínio técnico para arquivos; oito rotas atuais e sites alheios preservados; relatório de divergências resolvidas.

**Não pode acontecer:** envio duplicado de emails/webhooks, indexação da cópia de teste, Pixel duplicado, quebra do Elementor ou alteração de licença sem confirmar titularidade.

Referências: [substituição segura com WP-CLI](https://developer.wordpress.org/cli/commands/search-replace/), [migração do Elementor](https://elementor.com/help/site-migration/), [URLs e licença](https://elementor.com/help/i-changed-the-url-of-my-website-and-elementor-does-not-work-anymore/).

### 4. Trocar o atendimento do domínio com retorno preparado

Combinar janela curta de congelamento das edições e, se houver dados dinâmicos, das gravações pertinentes. Exportar estado final consistente e sincronizar uploads; verificar a diferença desde o primeiro backup. Preparar mudança de cadastro/roteamento e SSL. Como o domínio já aponta à hospedagem, não assumir que uma nova mudança de DNS seja necessária.

Retirar os encaminhamentos ao GHL somente quando os destinos locais estiverem aprovados. Liberar administração e APIs do WordPress no domínio correto, preservar parâmetros e métodos POST, conferir raiz/www, páginas novas, antigas e 404. Manter email, alunos e `eduparmeggiani.com.br` fora da alteração. Conferir rastreamento e remover a proteção de testes no momento correto.

**Tem que fazer:** verificações públicas após a troca, um único produtor de tarefas, HTTPS válido e monitoramento de erros/formulários.

**Não pode acontecer:** intervalo sem site por remoção prematura do alias, perda de gravações ou modificação de registros de email/serviços alheios.

Retorno: restaurar cadastro, pasta e regras anteriores, reabrindo os encaminhamentos para o GHL e preservando as páginas estáticas. Preferir reversão de roteamento; não restaurar cegamente um banco antigo sobre dados novos. Se houver gravações depois da troca, congelar e reconciliar essas gravações antes de reabrir o antigo. A origem permanece disponível durante o período de observação.

### 5. Confirmar independência e retirar a cobrança de WordPress

Observar pelo menos um ciclo real de uso e de backup; referência de planejamento de 7 dias, estendida se fluxos importantes ainda não ocorreram. Testar acesso às páginas com o domínio técnico bloqueado no cliente para detectar dependências residuais. Confirmar restauração do backup próprio, renovação HTTPS, licenças e funcionamento das integrações que continuarão no GHL.

**Tem que fazer:** comprovação de independência da hospedagem WordPress antiga, cópia final externa e identificação exata do item de cobrança que pode ser encerrado. Calcular economia mensal líquida = cobrança removida − custos novos recorrentes, incluindo licenças anuais divididas por 12; contabilizar manutenção e custo único separadamente.

**Não pode acontecer:** cancelar conta/subconta GHL usada por outras funções, perder DNS administrado por esse serviço, apagar origem/backup antes do aceite ou prometer economia sem verificar a fatura. O pedido atual não autoriza cancelamento; a futura operação deve ter escopo explícito do serviço a encerrar.

## Alternativas de acesso e próximos insumos

1. Preferido: obter/reutilizar SSH na origem e destino; conduzir exportação, transferência e restauração pelo terminal, administração por API.
2. Se a origem só permitir SFTP: copiar arquivos e obter exportação completa do banco por recurso suportado ou plugin de backup. Confirmar formato portátil, tamanho e limites/custo antes de escolher plugin.
3. Se não houver exportação por terminal/API: usar painel pontualmente para gerar o pacote ou habilitar acesso. Não depender de endpoints internos não documentados nem instalar scripts públicos de administração para contornar falta de acesso.

Para transformar o plano em execução faltam: acesso SSH/WP administrativo da origem; disponibilidade atual do acesso WHM/cPanel e SSH do destino; inventário autenticado e medição de capacidade; licença do Elementor e cobrança específica do WordPress. A precedência das oito páginas novas já foi confirmada. Não são necessários todos esses dados para concluir a viabilidade preliminar, mas são necessários antes da troca.

Não foi instalado plugin, exportado banco, alterado servidor ou aberto navegador nesta sessão. Somente este plano foi criado. Verificação: consultas públicas GET, comparação com configuração local e fontes oficiais. Tempo total e consumo real de tokens: indisponíveis no ambiente como métricas por tarefa; nenhuma estimativa apresentada como medição.
