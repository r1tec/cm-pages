# Nova conta WordPress lp.eduparmeggiani.com

13/09/2026. Pedido: criar conta nova após recusa do suporte à renomeação; migrar e ativar. Substitui a espera pela alteração de `eduwpcom`. Não contratar pacote adicional nem cancelar contas.

1. Criar conta `edulp`, domínio `lp.eduparmeggiani.com`, no pacote existente `poolocom_Basico`; guardar senha em armazenamento privado antes da chamada. Conferir existência antes de repetir chamadas. Aceite: conta isolada e acessos funcionais; não alterar contas existentes.
2. Transferir arquivos e banco para raiz/banco exclusivos, preservar backup externo e proteções. Conferir sincronização com origem GHL. Aceite: hashes e inventário, restauração funcional; não sobrescrever bancos alheios nem disparar integrações durante testes.
3. Ajustar URLs serializadas e PHP, excluir cópias estáticas do atendimento local e encaminhar as oito rotas de LP às páginas originais; DNS e HTTPS de LP. Aceite: editor, mídia, páginas e checkout sem compra real; não mudar slugs nem conteúdo das páginas em tráfego.
4. Com LP aprovado, trocar somente destinos GHL do bloco de encaminhamentos da conta original, preservando parâmetros, métodos e demais regras. Aceite: nove rotas e raiz atendidas no novo WP, oito páginas estáticas inalteradas; backup e reversão do bloco preparados, nenhum loop.
5. Verificar operação e backup, documentar pendências de licença e observação de sete dias. Não cancelar GHL ou apagar contas/backups sem autorização específica.

Detalhes de ativação: `ATIVACAO-WORDPRESS-LP.md`, adaptando conta de destino para `edulp`. O registro DNS externo `lp` não resolvia na consulta inicial de 13/09. O token DNS disponível anteriormente não via esta zona; verificar acesso antes de pedir dado repetido.

## Aceites obrigatórios

**Tem que fazer:** conta e banco exclusivos; backup privado íntegro; restauração testada; domínio e certificado válidos; validação das rotas, editor e parâmetros antes de trocar destinos; retorno preparado.

**Não pode acontecer:** alterar arquivos das oito páginas em tráfego, remover alias do domínio principal, sobrescrever banco existente, publicar backup/segredos, disparar integrações pela cópia de teste, contratar serviço extra ou cancelar GHL.

## Progresso

**Ativação realizada em 13/09/2026.** Conta `edulp`, banco efetivo `edulp_eduwpcom_site`, HTTPS válido. API cPanel, SFTP e tarefas privadas no cron permitiram concluir sem shell SSH. URLs serializadas ajustadas; usuário confirmou login/editor. Proteções de teste removidas, administrador definitivo privado, tarefas e backup diário configurados. Raiz e nove rotas antigas agora encaminham para LP; oito HTMLs de tráfego idênticos antes/depois. 22 verificações públicas aprovadas.

Observação mínima até 20/09/2026, licença Elementor, recebimento de eventos externos e cancelamento específico da cobrança ainda pendentes. Provas, backups e retorno em `EXECUCAO-wordpress-ghl.md`. Não repetir criação/importação; contas e origem antigas preservadas.
