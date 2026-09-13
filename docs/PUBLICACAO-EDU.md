# Publicação nas duas contas

## Decisão vigente — WordPress em lp.eduparmeggiani.com

O usuário decidiu manter `eduparmeggiani.com` como alias da conta `contemmagia`.
O suporte trocará apenas o domínio principal da conta `eduwpcom` para
`lp.eduparmeggiani.com`. As oito páginas estáticas permanecem na conta original.
O espelhamento está **desativado** em `config/edu-publicacao.json`: não é mais
necessário manter essas páginas na conta WordPress. Isso não desativa a publicação
normal na conta Contém Magia. As cópias de teste já existentes não foram apagadas.

Os procedimentos abaixo descrevem a arquitetura anterior e ficam apenas como
referência de reversão. Não reativar o espelhamento na arquitetura atual.

## Arquitetura anterior — referência

O comando continua sendo `./publicar.sh <slug>`. Para as oito rotas migradas,
ele publica na conta Contém Magia e espelha a versão entregue para `eduwpcom`.
Os modos de ajuste de GTM também espelham quando usados com `--aplicar`.

`config/edu-publicacao.json` controla a ativação. `espelhar_edu.py` é auxiliar
interno do publicador; não substitui o fluxo de publicação e não recompila HTML.
Usa Paramiko no Python local. Credenciais e host keys ficam em
`~/.config/cm-pages/credentials/`, fora do Git.

Para conferir ou recuperar somente o espelho, preservando edições locais:

```sh
./publicar.sh --espelhar-edu bce coe drb mce mpg gdp ecm-26 ecm-26-v1
./publicar.sh --espelhar-edu --aplicar bce coe drb mce mpg gdp ecm-26 ecm-26-v1
```

O auxiliar aceita somente essas oito rotas, rejeita links e caminhos externos
nos arquivos de transferência, verifica o hash e guarda a versão anterior em
`/home/eduwpcom/.cm-publish-backups/`. Não toca nas pastas do WordPress.
Se o segundo envio falhar, o comando termina com erro; retome pelo modo acima.

No WordPress, `config/wp-cm-pages.php` deve ser instalado como mu-plugin.
Ele retira as versões WordPress dessas oito rotas do sitemap de páginas e
adiciona um sitemap das versões estáticas. As versões antigas continuam no
banco para edição; as pastas estáticas têm precedência no atendimento HTTP.

O estado da troca do domínio e os testes estão em `EXECUCAO-wordpress-ghl.md`.
