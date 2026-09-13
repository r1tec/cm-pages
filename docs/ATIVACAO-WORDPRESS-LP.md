# Ativação do WordPress em lp.eduparmeggiani.com

**Ativado em 13/09/2026.** Usuário confirmou login/editor; 22 verificações públicas passaram após a troca. Oito páginas estáticas preservadas por hash. Procedimento abaixo fica como histórico operacional; não repetir criação, importação ou ativação. Estado atual e pendências pós-migração em `EXECUCAO-wordpress-ghl.md`.

Estado em 13/09/2026: suporte recusou renomeação. Usuário autorizou criar conta nova e migrar até ativação. Nova conta **edulp** criada com domínio `lp.eduparmeggiani.com`; usar essa conta em todas as etapas abaixo, em substituição a `eduwpcom`. Conta antiga permanece preservada.
Autorização vigente: executar plano `PLANO-CONTA-LP.md`; preservar páginas em tráfego. Shell da nova conta está desativado; SFTP e API funcionam. DNS `lp` ainda não resolvia na primeira verificação.

## Resultado definido

- Conta `contemmagia`: permanece responsável por `eduparmeggiani.com` (alias), `www` e pelas oito páginas estáticas.
- Conta `edulp`: WordPress independente em `lp.eduparmeggiani.com`; `eduwpcom` preservada como cópia anterior.
- Raiz e nove rotas antigas do domínio principal terão encaminhamento para `lp`, visível no navegador, em substituição ao GHL. Nenhuma alteração de DNS do domínio principal.
- Rotas preservadas: `bce`, `coe`, `drb`, `mce`, `mpg`, `gdp`, `ecm-26`, `ecm-26-v1`, inclusive arquivos e URLs com campanha.
- Rotas WordPress encaminhadas: `iat`, `mpp`, `t3x`, `wmpp-obrigado`, `bpa`, `bco`, `6-edb`, `6-edb-obrigado`, `drb-vsl`.

## Antes de qualquer ativação

1. Consultar domínio principal efetivo de `edulp` pelo WHM; deve ser `lp.eduparmeggiani.com`. Não depender da renomeação de `eduwpcom`.
2. Confirmar DNS público de `lp` apontando para `187.108.194.90` e TLS com cadeia/hostname válidos. Emitir AutoSSL se necessário. Não presumir que o suporte criou DNS externo.
3. Confirmar document root `/home/edulp/public_html`, banco `edulp_eduwpcom_site`, PHP 8.3 e acesso administrativo. Reutilizar credenciais privadas `conta-edulp.json` e `wordpress-edulp.json`; não pedir novamente. SFTP, API cPanel e cron oficial substituíram o SSH na execução.
4. Guardar backup privado dos arquivos e banco atuais e do `.htaccess` efetivo da conta original. Validar quota antes de acumular novos pacotes.
5. Comparar origem com backup e sincronizar conteúdo final na cópia protegida, sem sobrescrever a configuração de conexão, regras de isolamento e ajustes de hospedagem. Não importar SQL cegamente após edições locais.

## Preparação no novo endereço

- Simular e aplicar substituição serializada de `https://migracao-wp.eduparmeggiani.com` por `https://lp.eduparmeggiani.com` apenas no banco da cópia, preservando GUIDs. Conferir também referências residuais ao GHL fora de GUIDs.
- Regenerar CSS do Elementor e verificar recursos sem depender do domínio técnico.
- Arquivar as oito pastas estáticas de teste fora de `public_html`, sem removê-las na conta original. Configurar redirecionamentos GET/HEAD dessas rotas em `lp` para o domínio principal com query string preservada; impedir que POST seja convertido silenciosamente em GET. A raiz e nove rotas WordPress de `lp` não podem voltar ao domínio principal, evitando loop.
- Adaptar o MU-plugin `cm-pages.php`: manter exclusão das páginas WP sobrepostas, retirar o sitemap de cópias estáticas em `lp`. Preservar as páginas e slugs originais no banco.
- Testar login, editor e prévia; conferir páginas no celular/desktop, mídia, 404 e REST. Não usar HTTP 200 isolado como prova funcional.
- Conferir checkouts/links de campanha sem compra real. Identificar licença válida do Elementor: último estado em cache era `cancelled`, embora o editor abra. Não comprar nem ativar licença sem titularidade confirmada.
- Definir backups recorrentes e renovação HTTPS; validar restauração. A cópia portátil original já foi restaurada; o pacote adicional de 11/09 tem hashes verificados, não teste de restauração próprio.

## Troca de encaminhamentos, somente com destino pronto

1. Guardar baseline público das oito rotas estáticas e seus links, parâmetros e rastreamento.
2. No WordPress `lp`, remover administrador temporário de QA e proteções de teste na ativação; reativar somente tarefas necessárias, evitando dois produtores de disparos.
3. Ler e salvar `.htaccess` remoto atual da conta `contemmagia`. Dentro do bloco delimitado `CM migration eduparmeggiani.com`, trocar exclusivamente os destinos GHL da raiz e das nove rotas por `https://lp.eduparmeggiani.com`. Manter inicialmente 302 para permitir reversão rápida. Preservar todo o restante do arquivo.
4. Conferir diff: zero mudanças nas regras das oito páginas e nos sites alheios. Se o bloco remoto divergir da estrutura esperada, investigar antes de enviar.
5. Testar raiz, www, nove rotas, oito estáticas, arquivos, 404 e query strings. Confirmar ausência de loops e HTTPS válido. Publicações estáticas continuam exclusivamente pelo publicador normal; espelhamento `eduwpcom` fica desativado.

## Retorno e encerramento

Se houver falha, restaurar somente os destinos anteriores do bloco de encaminhamentos a partir do backup, preservando alterações concorrentes. Não restaurar banco antigo sobre gravações novas.

Manter origem e backups por pelo menos sete dias após ativação e um ciclo real de uso/backup. Não cancelar assinatura GHL, DNS ou licenças. Identificar separadamente a cobrança de hospedagem WordPress e obter autorização específica para encerrá-la.

## Provas e acessos

Estado e backups: `docs/EXECUCAO-wordpress-ghl.md`. Credenciais em `~/.config/cm-pages/credentials/`, fora do Git. Nenhum segredo neste documento.
