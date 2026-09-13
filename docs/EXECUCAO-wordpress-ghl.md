# Execução da migração WordPress

13/09/2026 — WordPress ativado em lp.eduparmeggiani.com; encaminhamentos antigos trocados e testes públicos aprovados. Observação pós-migração e encerramento da cobrança ainda pendentes. Compra de serviços e cancelamento de item ainda não identificado continuam pendentes de decisão específica.

Plano: `docs/PLANO-wordpress-ghl-hospedagem-propria.md`.

## Estado comprovado

### Ativação concluída — 13/09/2026

- Usuário confirmou manualmente login e Elementor funcionando no domínio LP. Esse aceite resolveu o bloqueio de verificação humana do navegador automatizado.
- WordPress em **https://lp.eduparmeggiani.com**, conta `edulp`, banco `edulp_eduwpcom_site`. Proteções de teste retiradas, ambiente production, indexação habilitada; HTTP externo e manutenção de plugins reabilitados. HTTPS válido.
- Administrador definitivo criado; credencial privada em `~/.config/cm-pages/credentials/wordpress-admin-lp.json`. Administrador temporário de QA removido. Administradores originais preservados.
- Apenas dois destinos GHL foram trocados no bloco de `.htaccess` da conta `contemmagia`: raiz e nove slugs antigas agora encaminham a LP com 302, preservando parâmetros. Alias, DNS principal, outras contas e regras das oito páginas mantidos. Troca por rename SFTP com conferência de concorrência.
- Oito HTMLs de páginas em tráfego têm SHA-256 idêntico imediatamente antes/depois. Provas e configurações de retorno em `~/.local/share/cm-pages/backups/lp-ativacao-20260913`, incluindo `cutover.json` e `imediatamente-antes.htaccess`.
- **22 verificações públicas passaram:** dez encaminhamentos e destinos (raiz + nove rotas), oito páginas estáticas, www, REST, sitemap e 404. Parâmetros UTM/fbclid preservados. Resultados em `/private/tmp/cm-stage-browser/lp/public-final.json`.
- Cron automático da origem GHL suspenso em wp-config, com cópia anterior privada para retorno. No novo WP, cron automático por visita permanece suspenso e execução agendada a cada cinco minutos foi instalada. Backup diário às 03:17 no horário do servidor, retenção aproximada de três dias; backup inicial externo conferido. Backup final de produção solicitado; confirmar conclusão e cópia externa.
- **Ainda não encerrado:** período de observação de sete dias após a ativação (referência mínima 20/09/2026), um ciclo real de uso/backup, licença Elementor Pro (cache indicava cancelled), comprovação de recebimento de eventos externos, automação da cópia externa recorrente e identificação/cancelamento específico da cobrança WordPress. Não cancelar GHL, apagar origem nem prometer licença/economia confirmada.
- Os estados de espera abaixo são históricos e não substituem esta ativação.
- Backup final de produção terminou com código 0; cópia externa em `~/.local/share/cm-pages/backups/lp-producao-20260913-114002`, banco e arquivos conferidos por SHA-256. Tarefa temporária removida; permanecem somente backup diário e cron WordPress recorrentes. Provas públicas, capturas e auxiliares também preservados em `lp-ativacao-20260913/provas`, fora de `/tmp`.
- Consumo real de tokens e tempo total da tarefa não disponíveis como métricas do ambiente; sem estimativas apresentadas como medição.

### WordPress LP preparado e testes públicos protegidos — 13/09

- Certificado TLS de `lp.eduparmeggiani.com` validado sem ignorar erros, vencimento 12/12/2026. PHP 8.3.19, extensões mbstring e nd_mysqli habilitadas na conta `edulp`.
- Agendador oficial cPanel API2 Cron permite tarefas privadas sem SSH. Diagnóstico e ajuste foram executados com trava de execução única; tarefas concluídas removidas. Primeira tentativa de ajuste parou antes de tocar no banco por falta de mysqli; extensão corrigida e nova tentativa terminou com código 0.
- WP-CLI confirmou instalação; substituição serializada do endereço temporário para LP simulada e aplicada, **2992 substituições em ambas**, GUIDs preservados. Home LP, 34 páginas; flush de CSS Elementor concluído.
- Cópia movida de `.wp-restore-api` para `/home/edulp/public_html`; raiz inicial guardada em `.public-html-inicial`. Credenciais de banco e salts ajustados, handler PHP do cPanel preservado. Autenticação HTTP, noindex e bloqueio de disparos continuam ativos.
- Oito pastas estáticas da cópia arquivadas em `/home/edulp/.estaticas-preservadas`. LP encaminha essas rotas para as páginas originais, com parâmetros. Sitemap de cópias estáticas retirado; exclusão das páginas WP sobrepostas mantida. Nenhuma slug ou página da conta original alterada.
- Teste Playwright LP: raiz e nove páginas 200, inexistente 404, nenhuma imagem quebrada reportada nessas navegações. Oito redirecionamentos 302 conferidos com `utm_source` e `fbclid` preservados. Capturas desktop/mobile e resultados em `/private/tmp/cm-stage-browser/lp`.
- Login LP apresenta Human verification no navegador automatizado. Janela visível aberta e usuário solicitado a concluir CAPTCHA; login/editor LP ainda não aceitos. Não contornar a verificação nem ativar com esse teste pendente.
- Baseline dos oito HTMLs e `.htaccess` original preservados em `~/.local/share/cm-pages/backups/lp-ativacao-20260913`. Candidato altera somente duas ocorrências de destino GHL dentro do bloco delimitado. **Candidato ainda não enviado**; conferir arquivo remoto novamente antes de aplicar.
- Backup inicial LP iniciado pelo cron em `/home/edulp/.wp-backups`, script privado `.migracao-preparada/backup.sh`, fonte `config/backup-wordpress-lp.sh`. Confirmar saída, transferir cópia externa e remover tarefa inicial; agendamento recorrente ainda não configurado. Não declarar migração concluída nem iniciar contagem de sete dias.
- Backup inicial terminou com código 0, pasta `20260913-112602`. SQL compactado e arquivos baixados para `~/.local/share/cm-pages/backups/lp-20260913-112602`, SHA-256 de ambos conferidos. Tarefa inicial removida. Backup diário solicitado para 03:17 no horário do servidor, retenção de aproximadamente três dias no servidor; cópia externa recorrente ainda não automatizada. Backup portátil externo atual está preservado.

### Alternativa sem shell comprovada — 13/09

- DNS `lp` cadastrado pelo usuário e confirmado no servidor autoritativo: `187.108.194.90`. AutoSSL iniciado para `edulp`; certificado ainda a conferir.
- API2 oficial `Fileman::fileop` extraiu o pacote com sucesso em `/home/edulp/.wp-restore-api`, pasta privada. Nada foi extraído sobre o site público.
- UAPI `Backup::restore_databases` importou o SQL compactado via parâmetro `backup`, após retirar somente o cabeçalho sandbox incompatível. Log `/home/edulp/.cpanel/logs/restoredb/2026-09-13T14:12:55Z.1.log` registra `restore_done` e sucesso.
- **Nome efetivo do banco restaurado: `edulp_eduwpcom_site`**, determinado pelo cPanel a partir do dump; não `edulp_site` (banco vazio criado anteriormente). Ambos pertencem à nova conta. Usuário `edulp_site` vinculado ao banco restaurado e arquivo privado de credenciais atualizado. Não importar novamente cegamente nem usar nome antigo nas próximas etapas.
- Shell não é bloqueio para extração/importação: caminho administrativo oficial funcionou. Ajustes de URLs serializadas, configuração, PHP/extensões, HTTPS e testes ainda pendentes antes de ativar. Nenhum redirecionamento público alterado.

### 13/09/2026 — conta nova criada após recusa de renomeação

- Usuário autorizou criar nova conta `lp.eduparmeggiani.com`, migrar e ativar. Plano em `PLANO-CONTA-LP.md`; não aguardar renomeação nem transferir alias do domínio principal.
- WHM `createacct` confirmou **Account Creation Ok**, conta `edulp`, pacote existente `poolocom_Basico`, quota 6000M. Credenciais guardadas privadamente antes da criação em `~/.config/cm-pages/credentials/conta-edulp.json` (0600). Não repetir criação.
- Banco e usuário **edulp_site** criados via UAPI, permissões atribuídas apenas nesse banco. Credencial em `wordpress-edulp.json` (0600). Banco ainda não importado neste ponto.
- Login SSH autentica, mas o comando retorna **Shell access is not enabled on your account**. Mesmo resultado na antiga conta `eduwpcom`, cujo shell funcionou em 11/09. SFTP na conta nova funciona. Não interpretar autenticação ou código de saída 0 desse aviso como shell funcional.
- Solicitado ao usuário liberar shell somente de `edulp` e criar DNS A `lp` para `187.108.194.90`. DNS ainda não resolvia na consulta inicial. As outras contas e os apontamentos públicos não foram alterados.
- Transferência SFTP do backup validado de 11/09 para `/home/edulp/.migracao-preparada` iniciada, fora da raiz pública. Confirmar conclusão e hashes remotos antes de extrair/importar. A transferência não equivale a restauração nem sincronização final.
- Transferência concluída: SQL 227809759 bytes, pacote WordPress 447519561 bytes; tamanhos e SHA-256 de ambos confirmados por releitura SFTP. A conferência do pacote terminou antes de o pedido de interrupção chegar; processo concluiu com código 0. Originais locais de ambos também passaram na conferência SHA-256 anterior ao envio.
- PHP 8.3 configurado via UAPI somente no vhost `lp.eduparmeggiani.com`. Extensões e funcionamento web permanecem para validação após restauração. Nenhuma importação foi executada ainda.

### Decisão vigente — aguardar renomeação para lp, preservar tráfego

- Usuário abriu ticket com prazo informado de 24 horas para trocar **somente** o domínio principal da conta `eduwpcom`, de `migracao-wp.eduparmeggiani.com` para `lp.eduparmeggiani.com`. Não transferir o alias `eduparmeggiani.com` entre contas. Essa decisão substitui o plano anterior de transferência.
- Prioridade explícita: não alterar as páginas recebendo tráfego. As oito rotas estáticas continuam na conta `contemmagia`; os redirecionamentos públicos atuais permanecem para o GHL até validação do novo endereço.
- Espelhamento futuro desativado localmente (`config/edu-publicacao.json`), pois a arquitetura nova não precisa de cópias estáticas na conta WordPress. Nenhuma página publicada foi alterada por essa preparação.
- Após renomeação: validar DNS A `lp` para `187.108.194.90`, HTTPS, atualizar URLs serializadas somente no banco `eduwpcom_site`, regenerar CSS e repetir login/editor/rotas. Manter autenticação, noindex e bloqueio de disparos até a ativação.
- As cópias estáticas no novo WordPress devem ser arquivadas fora da raiz pública antes da ativação de `lp`; substituir sua precedência por encaminhamento explícito das oito rotas de `lp` às URLs originais em `eduparmeggiani.com`. Não alterar as slugs antigas no banco. Remover o sitemap `cmpages` da cópia, mantendo exclusão das páginas antigas sobrepostas para evitar divulgação duplicada.
- Somente depois das provas, atualizar os dois destinos do bloco de redirecionamentos na conta original (raiz e nove slugs antigas) do GHL para `https://lp.eduparmeggiani.com`. Preservar regras das oito páginas, métodos e parâmetros. Fazer backup do `.htaccess` remoto efetivo e comparar antes de aplicar; não sobrescrever configurações concorrentes com uma cópia local antiga.
- Plano operacional preparado em `docs/ATIVACAO-WORDPRESS-LP.md`. Nenhuma troca de URL do banco, remoção de proteção ou alteração remota de roteamento é antecipada ao ticket.

### 11/09/2026 — HTTPS e editor validados

- Registro público de `migracao-wp.eduparmeggiani.com` criado pelo usuário; resolução confirmada. Certificado HTTPS validado pelo cliente TLS com verificação de cadeia e hostname, sem ignorar erros, vencimento em 09/12/2026. AutoSSL acionado novamente via UAPI com sucesso. Problemas reportados para nomes auxiliares sem DNS não incluem o hostname de teste.
- Login WordPress com administrador temporário funcionou no teste automatizado. Elementor da página 1715 abriu com painel e iframe de pré-visualização presentes; captura em `/private/tmp/cm-stage-browser/final-account/editor.png`. Isso prova abertura do editor, não salvamento de alterações.
- SSH da conta eduwpcom revalidado. WHM `myprivs` ainda retorna `edit-account=0`; solicitada ao usuário a liberação específica pelo suporte, preservando alias, arquivos e DNS até a sincronização final.
- Os bloqueios históricos de DNS, certificado e verificação humana não impedem mais estes testes. Troca pública ainda não executada.
- Novo backup de banco e arquivos da cópia validada salvo fora do servidor e do Git em `~/.local/share/cm-pages/backups/eduwpcom-validado-20260911-092650`, com permissões privadas e SHA-256 local igual ao remoto para os dois arquivos. Não substitui a sincronização final nem o teste de restauração desse novo pacote.
- Origem e cópia têm 34 páginas publicadas/rascunhos; última data de alteração em ambas: `2026-09-10 10:57:19`. Igualdade de contagem/data não equivale a comparação integral de conteúdo.
- Configuração em cache da licença Elementor Pro reporta `success=false`, `error=cancelled`. Editor abre, mas não foi comprovada licença válida para atualizações; não ativar chave, contratar nem remover plugins por inferência. Titularidade e licença própria permanecem pendentes.

### Atualização mais recente — restauração e bloqueio no acesso ao editor

- WordPress e as 29 tabelas restaurados na conta **eduwpcom**, em `/home/eduwpcom/public_html`, com banco exclusivo. PHP 8.3 configurado somente nessa conta; extensões mbstring e nd_mysqli habilitadas.
- Cópia usa o endereço temporário `migracao-wp.eduparmeggiani.com`, autenticação HTTP e noindex. Os testes direcionaram esse nome ao IP da hospedagem localmente; não comprovam DNS nem certificado público desse endereço.
- E-mails, chamadas HTTP externas do WordPress e cron bloqueados durante a preparação. Plugins específicos da hospedagem de origem desativados na cópia.
- Oito páginas estáticas copiadas do site publicado pelo fluxo `publicar.sh --espelhar-edu --aplicar`; 178 arquivos, com verificação de integridade. Publicações futuras dessas rotas passam pelo espelhamento configurado em `config/edu-publicacao.json`.
- Testes HTTP no servidor novo: 18 rotas de páginas responderam 200; caminho inexistente respondeu 404; API WordPress respondeu 200. Isso não comprova funcionamento de pagamentos nem envio de formulários externos.
- MU-plugin de sitemap instalado: oito URLs estáticas e exclusão de cinco páginas WordPress sobrepostas verificadas pelo WP-CLI. XML público ainda precisa ser verificado após a configuração final de indexação.
- **Editor ainda não validado:** `/wp-login.php` apresenta verificação humana antes do formulário WordPress. O usuário tentou concluir na janela Chrome aberta para o teste e informou falha. Não repetir automaticamente nem contornar a verificação. A liberação SSH não resolveu esse bloqueio HTTP.
- Administrador temporário de QA foi criado (ID 4), com credenciais privadas; remover antes da publicação definitiva. Não houve edição de página pelo painel.
- **Troca do domínio ainda pendente:** o token WHM retornou negação real para `modifyacct`; não remover o alias da conta antiga sem caminho confirmado para atribuir o domínio à conta nova. Nenhum redirecionamento público foi removido.
- SSL existente foi preservado em backup privado. A sincronização final, validação do editor, licenças, operação externa, certificado/renovação e ciclo de backup permanecem pendentes. O período de observação começa depois da troca.
- Os registros abaixo são históricos; estados antigos de espera por SSH e restauração foram superados por esta atualização.

### SSH da conta nova validado após liberação de Marcos/TurboCloud

- Conexão autenticada com sucesso em `br.midgard4010.com.br:215`, usuário **eduwpcom**, usando a senha cPanel já guardada em `~/.config/cm-pages/credentials/conta-eduwpcom.json`. Não solicitar novamente esses dados.
- Prova remota: `whoami` → `eduwpcom`; `pwd` → `/home/eduwpcom`; PHP e WP-CLI em `/usr/local/bin`, cliente MySQL em `/usr/bin/mysql`; comando terminou com código 0.
- Teste realizado via Paramiko com validação da chave do servidor no known_hosts já registrado. Nenhum arquivo remoto ou configuração alterado neste teste.
- A pendência de SSH da conta nova está resolvida. Próximo passo da migração: transferir/restaurar a cópia na conta **eduwpcom**, mantendo proteção de teste, e validar ali o servidor HTTP/PHP definitivo. A cópia anterior em `contemmagia` não é a instalação final. A transferência do domínio principal continua pendente e não deve anteceder os testes e preservação das oito rotas estáticas.

### Decisão de arquitetura — conta própria para eduparmeggiani.com

- Instrução mais recente: o usuário pediu explicitamente tentar criar a conta e informar erro real, sem exigir consulta prévia ao suporte sobre limite. Essa autorização substitui a espera anterior por confirmação de capacidade; não inclui contratar outro plano.
- Tentativa em andamento: usuário cPanel `eduwpcom`, domínio de preparação `migracao-wp.eduparmeggiani.com`, pacote existente `poolocom_Basico`, `forcedns=0`, sem privilégios de revenda. O alias público `eduparmeggiani.com` permanece na conta original.
- Resultado confirmado: **conta criada**, `createacct result=1 / Account Creation Ok`; `accountsummary` revalidou usuário `eduwpcom`, domínio temporário, pacote `poolocom_Basico`, quota 6000M e conta ativa. A resposta de criação contém log HTML em `metadata.output`; não exibi-lo, pois pode incluir dados operacionais sensíveis. Mostrar apenas `result`, `reason`, `command`.
- Tentativa real de habilitar SSH na conta nova: `modifyacct user=eduwpcom HASSHELL=1` retornou `result=0 / Permission denied: You do not have the required privileges to run modifyacct`. Nenhuma habilitação ocorreu. O SSH liberado pelo suporte continua válido para `contemmagia`, não para a nova conta.
- Criação não foi barrada por quota. Não foi solicitado upgrade nem contratado serviço pelo agente; não usar esse resultado como auditoria da fatura. O domínio público e seus encaminhamentos seguem na conta antiga, e a restauração validada permanece em sua pasta privada anterior até transferência para a conta nova.
- Credencial gerada e guardada em `~/.config/cm-pages/credentials/conta-eduwpcom.json` (0600), antes da chamada de criação. Não repetir criação cegamente se houver timeout; consultar existência primeiro.
- Particularidade observada: `listaccts` retorna `result=0` e `reason="No accounts found."` quando o usuário buscado não existe. Isso confirma ausência, não falta de permissão. WHM API 1 deve receber `api.version=1` na URL.

- Usuário indicou `eduparmeggiani.com.br` como opção e autorizou, se fizer sentido, levar `eduparmeggiani.com` a uma conta própria. Preferência técnica: conta própria para `.com`, preservando `.com.br` e `contemmagia.com.br`.
- Inspeção somente-leitura da alternativa: conta `eduparmeggiani`, domínio principal `.com.br`, 252M usados, duas caixas de email, sem aliases/adicionais, shell desativado. Não é uma conta vazia. Nenhum email ou arquivo foi alterado.
- WHM permite `create-acct`, mas `resellerstats` retornou falta de privilégios; capacidade/limite de novas contas e eventual custo não foram confirmados. `edit-account=0` impede presumir renomeação de domínio principal pela API. Não criar conta nem remover alias até resolver o preparo e a troca controlada.
- Plano concreto da separação: preparar primeiro conta independente com endereço temporário autorizado e proteção; restaurar/testar nessa conta; preparar as oito rotas estáticas e adaptar o publicador único para atualizar ambos os destinos; preparar certificado e regras reversíveis; somente na janela final transferir `eduparmeggiani.com` do alias para domínio principal da conta pronta. A troca de domínio principal pode exigir ação do provedor dadas as permissões atuais.
- Impacto: regras atuais permanecem em `contemmagia/public_html/.htaccess` e não acompanham automaticamente o domínio. Nova conta deve receber regras correspondentes e páginas estáticas antes da troca. As rotas coincidentes continuam preferindo as oito páginas novas; raiz e demais rotas passam ao clone somente após testes. Não usar cópias manuais como manutenção permanente.
- Confirmar com provedor possibilidade de uma conta cPanel adicional sem novo custo e preparação/troca do domínio principal sem remover antecipadamente o alias. Não alterar DNS de email, `.com.br` ou alunos. Não foi criada conta nem alterado roteamento nesta decisão.

### SSH de destino e restauração — atualização após liberação do suporte

Resultados posteriores:

- Reteste com mbstring: `bco` e `bce` responderam 200. Conjunto das 15 rotas agora verificado com 200 e sem erros JavaScript; textos normalizados iguais em 15/15 comparações. Amostras desktop/celular capturadas para raiz, `6-edb` e `bce`. Isso não substitui testes de formulários, editor, licença, servidor HTTP definitivo e integrações.
- Diferenças em wp_postmeta explicadas por chaves de cache: `_elementor_css`, `_elementor_element_cache`, `_elementor_page_assets`; demais contagens por chave iguais. Túnel e servidores PHP temporários encerrados após os testes; podem ser reabertos com a configuração registrada. Cópia continua privada e com proteções ativas.
- Usuário perguntou sobre aproveitar outras contas já existentes no WHM. Esclarecido: não é necessário comprar domínio; uma conta vazia pode ser alternativa à liberação de domínio adicional. Aguardando indicação de qual conta está disponível e se há site/emails em uso, antes de inspecionar ou alterar esse território. Domínio final continua `eduparmeggiani.com`.

- Importação SQL concluída com exit 0; 29 tabelas presentes. Todas as contagens por tipo/status de conteúdo conferem: 14 páginas públicas, 20 rascunhos, 208 mídias e 1578 revisões, além dos outros tipos inventariados.
- WordPress e plugins originais iniciaram com PHP 8.3.19. Mu-plugins específicos da hospedagem antiga continuam desativados na cópia; bloqueios de HTTP, email e cron ativos.
- Simulação e aplicação da substituição serializada no banco de teste: 4828 ocorrências do domínio técnico para `http://127.0.0.1:18911`. Não é URL pública nem endereço de produção. Cache CSS do Elementor regenerado somente na cópia.
- Comparação posterior de registros: 26 de 29 tabelas com contagens iguais. Diferenças em `wp_options`, `wp_litespeed_url_file` e `wp_postmeta`, após alterações e regeneração de cache na cópia; confirmar diferenças por chave antes de aceitar integralmente. Nenhuma divergência de conteúdo principal encontrada até aqui.
- Chrome com rastreadores/envios bloqueados: origem respondeu 200 nas 15 rotas (raiz e 14 páginas). Primeira rodada da cópia: 13 rotas 200 e duas 500 (`bco`, `bce`), causadas por mbstring ausente no processo PHP 8.3. Extensão testada e disponível; reteste em andamento com `-d extension=mbstring`, sem alterar PHP compartilhado.
- Capturas e resumos de comparação em `/private/tmp/cm-stage-browser/results`; script `/private/tmp/cm-stage-browser/check.cjs`. Não representam validação de checkout, login/editor ou integrações externas. Mídia quebrada em `drb-vsl` apareceu também na origem sob as mesmas restrições de rede.
- Túnel privado atual: local 127.0.0.1:18911 → destino 127.0.0.1:18912. Servidor PHP temporário; não exposto publicamente. Fechar processos de teste ao encerrar.
- Solicitado ao usuário consultar suporte sobre liberar 1 domínio adicional sem custo, sem remover alias nem alterar DNS/arquivos. A arquitetura preferida continua dependendo dessa liberação; restauração isolada avançou independentemente.

- Suporte TurboCloud confirmou `br.midgard4010.com.br`, porta **215**, liberada para o IP público `187.34.190.232`. Não reutilizar a suposição anterior de porta 22.
- SSH autenticado como `contemmagia`; diretório `/home/contemmagia`. PHP, WP-CLI e cliente MySQL disponíveis. PHP CLI padrão 7.4.33; PHP alternativos 8.1, 8.2, 8.3.19 e 8.4 disponíveis. Não foi alterado o PHP dos sites existentes.
- A chave de destino fornecida em Downloads foi guardada, mas `ssh-keygen` rejeitou seu formato. Para resolver sem solicitar novo acesso, a pública de `/Users/raphaelmartins/.ssh/cm-pages-ghl-migracao-20260910.pub` foi importada e autorizada pelo token, com nome remoto `cm-migracao-4d6f58ba23.pub`. **Chave privada efetivamente funcional no destino: `/Users/raphaelmartins/.ssh/cm-pages-ghl-migracao-20260910`**.
- Hosts SSH conhecidos da sessão: origem `/private/tmp/cm-pages-ghl-known-hosts`; destino `/private/tmp/cm-pages-target-known-hosts`. Preservar/conferir fingerprints ao mover para armazenamento permanente.
- Backup original privado em `~/.local/share/cm-pages/backups/ghl-20260910-151341`: SQL 229216088 bytes, tar.gz 439552538 bytes. Validação: 12003 arquivos, todos com hashes correspondentes antes/depois da transferência, nenhuma mudança durante a cópia, nenhum link ou caminho inseguro; SQL contém 29 tabelas, sem eventos, triggers ou rotinas. `validation.json` guarda hashes dos artefatos. Ainda não representa aceite completo da etapa 2.
- Criados **somente para a restauração isolada**: pasta privada `/home/contemmagia/wp-edu-migracao-20260910` (fora de public_html), banco/usuário `contemmagia_edumig0910`. Credenciais persistentes privadas em `~/.config/cm-pages/credentials/stage-edu-20260910.json`; cliente remoto em `/home/contemmagia/.edu-migracao-mysql.cnf`, permissão 0600.
- Arquivos extraídos nessa pasta; config própria com cron e HTTP externo bloqueados; mu-plugins da origem e drop-ins desativados somente na cópia; guarda de testes bloqueia emails e chamadas HTTP. Sem URL pública, roteamento ou DNS alterados.
- Primeira importação abortou na linha 1: cliente MariaDB 10.5 não reconhece o cabeçalho de sandbox do dump 10.11. Nova importação em andamento, removendo em trânsito apenas a primeira linha reconhecida; original preservado. Scripts operacionais em `/private/tmp/cm-pages-restore-stage.py` e `/private/tmp/cm-pages-resume-import.py`. Não rodar novamente o criador: recursos já existem.
- Pendências após importação: comparação integral de tabelas/contagens, compatibilidade PHP/plugins, teste visual/funcional protegido, arquitetura pública e SSL, licenças/integrações, sincronização final e observação. O limite de domínios adicionais não foi alterado.

### Chaves persistentes — reutilizar sem solicitar novamente

- Origem SSH: `195.250.26.1`, porta 22, usuário `crhiznn`, chave privada `/Users/raphaelmartins/.config/cm-pages/credentials/origem-ghl.key` (cópia da chave de Downloads que autenticou com sucesso).
- Destino SSH: host da hospedagem `br.midgard4010.com.br`, conta `contemmagia`, chave privada `/Users/raphaelmartins/.config/cm-pages/credentials/destino-contemmagia.key` e pública no mesmo caminho com sufixo `.pub`. Fornecidas como `id_dsa`, mas a pública identifica algoritmo Ed25519. Porta SSH ainda não confirmada.
- Arquivos guardados fora do Git, com permissões 0600; cópias comparadas com os arquivos de origem. Nenhum valor secreto deve entrar em documentação, logs ou indexação.
- Após o usuário informar habilitação SSH, `accountsummary` ainda retornou `/usr/local/cpanel/bin/noshell` e a tentativa na porta 22 recebeu `Connection refused`. Não confundir chave cadastrada com shell habilitado. Aguardar confirmação de porta/liberação.
- `myprivs` autenticado: `allow-shell=0`, `allow-addoncreate=0`, `edit-account=0`, `create-acct=1`, `cpanel-api=1`. O token não permite resolver diretamente essas liberações. Não tentar contornar restrições com scripts públicos ou tarefas agendadas.
- Backup inicial da origem em andamento no diretório privado `/Users/raphaelmartins/.local/share/cm-pages/backups/ghl-20260910-151341`; exportação SQL concluída (229216088 bytes), validação e arquivos ainda pendentes neste registro. Script operacional local: `/private/tmp/cm-pages-backup-origin.py`.

### Token WHM disponibilizado

- Token `migracao-wordpress` fornecido pelo usuário e copiado de Downloads para `/Users/raphaelmartins/.config/cm-pages/credentials/whm-migracao-wordpress.token`, fora do Git. Diretório com permissão 0700 e arquivo 0600; igualdade da cópia conferida sem exibir conteúdo.
- Usuário informa que o token não expira. Validade e permissões remotas ainda não verificadas. Reutilizar esse arquivo privado; não solicitar novamente o valor nem incluí-lo em logs ou indexação.
- Confirmar endereço HTTPS e usuário WHM antes de enviar a credencial ao servidor.
- Endereço confirmado pelo usuário: `https://br.midgard4010.com.br:2087/`. Usuário WHM: `poolocom`. Reutilizar esses dados com o arquivo privado acima; não perguntar novamente. Esta confirmação resolve a pendência de endereço/usuário.
- Validação autenticada concluída: WHM `listaccts` e `accountsummary`, UAPI `DomainInfo::list_domains`, todos com resultados de leitura utilizáveis. O retorno UAPI está na chave raiz `result`, não em `data`/`cpanelresult`.
- Conta `contemmagia`, plano `poolocom_Basico`, ativa. Disco usado 2545M de 6000M; bancos ilimitados; domínios adicionais limitados a zero; shell `/usr/local/cpanel/bin/noshell`.
- Domínio principal `contemmagia.com.br`; `eduparmeggiani.com` confirmado como alias; nenhum domínio adicional; `alunos.contemmagia.com.br` preservado fora do escopo.
- Token permite as consultas cPanel testadas. Ainda não foram comprovadas permissões de criação de banco/domínio ou importação. Separação preferida continua condicionada à quota e ao acesso de execução no destino; não modificar pacote ou conceder shell sem avaliar privilégios e custos.

### Atualização: SSH da origem validado

- Autenticação concluída como `crhiznn`, usando a chave privada fornecida pelo usuário em `/Users/raphaelmartins/Downloads/contemmagiarsakey`. Permissões locais ajustadas para 0600; conteúdo não exibido. A chave gerada anteriormente nesta sessão foi recusada.
- Instalação localizada em `/home/crhiznn/public_html`; WP-CLI disponível em `/usr/local/bin/wp`.
- Leituras remotas: WordPress 7.1, PHP CLI 7.4.33, MariaDB 10.11.19. A versão PHP do servidor web ainda precisa ser conferida; não presumir que seja igual à do terminal.
- `wp db size --size_format=mb`: 194 MB. `du -sh`: 645 MB de arquivos. São medições iniciais, não prova de backup completo.
- Consulta `SELECT VERSION()` bem-sucedida confirma acesso de leitura ao banco. Exportação/importação ainda não testadas.
- Constante `MULTISITE` ausente no wp-config consultado; inventário completo ainda pendente.
- Espaço reportado por `df` pertence ao volume compartilhado; não comprova quota disponível da conta.
- Próximo impedimento: acesso administrativo do destino para validar isolamento, capacidade e banco exclusivo. Nenhuma alteração no site executada.

### Levantamento inicial (antes do fornecimento da chave)

- Configurações de FTP e Cloudflare encontradas localmente; autenticação remota não foi revalidada nesta execução.
- Credenciais GHL/WordPress e WHM/cPanel não encontradas no `.env` nem nas variáveis de ambiente consultadas. Nenhum valor foi exibido.
- Não há `~/.ssh/config`. Presença de variável do agente SSH não comprova acesso a nenhum dos servidores.
- Há alterações locais preexistentes em páginas e documentação; preservadas.
- Nenhum backup, restauração, alteração de produção ou cancelamento executado.
- Etapa 1 ainda não aceita: faltam inventário autenticado, capacidade, arquitetura validada, licenças e custos. Etapas 2–5 dependem desses resultados.

## Como disponibilizar os acessos

Não cole senhas ou tokens no chat. Use o `.env` local deste projeto, já usado pela operação, sem substituir as entradas existentes. Os nomes abaixo são convenções para esta migração. Se o acesso já estiver guardado em outro local privado, basta informar o caminho, sem o conteúdo.

### 1. Origem no GHL — necessário para começar o backup

1. Entre na subconta que contém o site `crhishmxlb.wpdns.site`.
2. Abra **Sites → WordPress**, selecione o site e abra **Advanced Settings → FTP/SSH Access**.
3. Copie os dados exibidos para novas entradas locais: `WP_SOURCE_SSH_HOST`, `WP_SOURCE_SSH_PORT`, `WP_SOURCE_SSH_USER` e `WP_SOURCE_SSH_PASSWORD`. Use a porta informada pelo painel.
4. Se houver somente SFTP ou não aparecer a seção, solicite ao administrador da subconta acesso SSH com WP-CLI e exportação completa do banco. SFTP sozinho não comprova acesso ao banco.
5. Confirme que consegue abrir a administração WordPress. O acesso independente do login automático do GHL será conferido antes da troca; não é necessário criar outro administrador antecipadamente.

Fonte: [SSH no HighLevel](https://help.gohighlevel.com/support/solutions/articles/155000005588-ssh-access-for-wordpress).

### 2. Destino — administração da hospedagem

1. Abra o cPanel da conta `contemmagia` pelo painel da hospedagem.
2. Procure **Security → Manage API Tokens** (Segurança → Gerenciar tokens de API).
3. Clique **Create**, nomeie `migracao-wordpress` e defina uma validade que cubra a migração e a observação posterior.
4. Salve localmente `WP_TARGET_CPANEL_URL` (endereço HTTPS do painel), `WP_TARGET_CPANEL_USER` e `WP_TARGET_CPANEL_TOKEN`. Copie o token antes de sair: o cPanel não volta a exibi-lo.
5. Se essa opção não existir, peça ao provedor para habilitá-la. Caso já possua o token WHM anterior em armazenamento privado, informe o caminho para reutilização e conferência das permissões; não é preciso criar acesso administrativo amplo sem necessidade.
6. Solicite ao provedor SSH da conta com host, porta e usuário, e autenticação por chave ou senha. Guarde como `WP_TARGET_SSH_HOST`, `WP_TARGET_SSH_PORT`, `WP_TARGET_SSH_USER` e `WP_TARGET_SSH_KEY_PATH` ou `WP_TARGET_SSH_PASSWORD`.

Fonte: [Tokens no cPanel](https://docs.cpanel.net/cpanel/security/manage-api-tokens-in-cpanel/).

Texto que pode enviar ao suporte:

> Preciso migrar um WordPress para uma instalação isolada nesta hospedagem, preservando o WordPress existente e as páginas estáticas da conta contemmagia. Preciso de SSH com acesso a arquivos e importação/exportação de banco, API do cPanel e confirmação de espaço/inodes, limites de recursos e bancos, versões de PHP e MySQL/MariaDB. eduparmeggiani.com está como alias; confirmem se posso usar uma raiz exclusiva e SSL com renovação automática. Houve limite zero de domínios adicionais anteriormente. Informem qualquer custo antes de alterar o plano. Não removam o alias nem alterem DNS ou arquivos agora.

### 3. Dados necessários antes da troca e do encerramento

- Onde está a licença do Elementor Pro e se pode ser usada fora do GHL.
- Valor e identificação do item de hospedagem WordPress na cobrança do GHL, sem dados de cartão.
- Local privado externo para guardar backups e responsável por sua manutenção.
- Momento permitido para suspender brevemente as edições na sincronização final.

## Continuidade

Com os acessos: validar conexões somente por leitura, inventariar toda a instalação e capacidade, decidir isolamento com base no resultado e prosseguir pelos aceites do plano. Manter públicas as oito páginas novas; não extrair arquivos sobre `public_html`. Não mudar roteamento antes da restauração testada. O período de observação começa após a troca, não nesta data; referência de sete dias e pelo menos um ciclo real de uso e backup.

A tentativa de indexar a descoberta de acessos foi rejeitada pela revisão automática por risco de divulgar dados sensíveis. A alternativa local retornou somente presença/ausência de configurações. Nenhuma autorização extra é necessária para retomar por esse método seguro.

Tempo total e consumo real por tarefa: indisponíveis. Nenhuma etapa foi declarada concluída sem suas provas.
