# Instruções para o Claude Code

Este pacote é um site estático pronto. Nada para compilar, nada para instalar.
A tarefa é publicar e deixar a publicação automática funcionando.

## O que tem aqui

```
coe/index.html                     a página, autocontida (3,7 MB)
.cpanel.yml                        recipe de deploy do cPanel Git
.github/workflows/deploy-ftp.yml   deploy por FTP a cada push
publicar.sh                        deploy manual por FTP, um comando
README.md                          instruções para humanos
```

`coe/index.html` já tem HTML, CSS, JS, fontes e imagens embutidos. Não mexa no
conteúdo dele: quando a página mudar, um arquivo novo é gerado no Claude Design
e substitui este.

## Tarefa 1: criar o repositório e subir

```bash
cd "Contem Magia Pages"
git init -b main
git add .
git commit -m "Página COE"
gh repo create contem-magia-pages --private --source=. --push
```

Se o `gh` não estiver autenticado: `gh auth login`.

Adicione um `.gitignore` com `.env` antes do primeiro commit. As credenciais de
FTP nunca entram no repositório.

## Tarefa 2: escolher o caminho de publicação

O painel da hospedagem é cPanel. O usuário viu a tela de Git Version Control com
o aviso "your system administrator must enable shell access to allow you to view
clone URLs", o que indica que o acesso shell está desativado na conta. Confirme:

- **Se houver acesso SSH/shell:** use o cPanel Git. No painel, Git Version
  Control > Criar, marque "Clone a Repository", informe a URL do repositório do
  GitHub e o caminho `/home/USUARIO/repositories/contem-magia-pages`. O
  `.cpanel.yml` deste pacote copia `coe/index.html` para
  `public_html/coe/` quando o usuário clicar em "Deploy HEAD Commit". Para
  automatizar, configure um webhook do GitHub que dispare o pull.

- **Se não houver shell (mais provável):** ignore o cPanel Git e use FTP. Duas
  opções, e vale montar as duas:

  1. `publicar.sh`, para publicar da máquina do usuário. Peça a ele o host, o
     usuário, a senha e a pasta do FTP, grave em `.env` (fora do git), instale
     o `lftp` e rode uma vez para validar. A partir daí, "publica" é
     `./publicar.sh`.

  2. O workflow `.github/workflows/deploy-ftp.yml`, para publicar a cada push.
     Cadastre os segredos no repositório:
     `gh secret set FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`, `FTP_DIR`.
     Teste com `gh workflow run "Publicar por FTP"`.

## Tarefa 3: validar

- Abrir `https://DOMINIO/coe` e conferir que a página carrega inteira, com as
  imagens e os prints de depoimento.
- Testar em 360px de largura: não pode haver rolagem horizontal.
- Clicar no botão e confirmar que vai para `https://pay.contemmagia.com.br/c/coe`.
- Verificar que o HTTPS está ativo no domínio.

## Travas de conteúdo, caso precise editar algo

- Texto do botão sempre `QUERO OUVIR MEUS GUIAS`, link sempre
  `https://pay.contemmagia.com.br/c/coe`
- A aula ao vivo nunca é descrita como recorrente: sempre "a próxima terça"
- O aviso de que a prática espiritual caminha ao lado do acompanhamento médico e
  psicológico aparece no FAQ e no rodapé, e não pode sair
- Nenhum preço aparece antes da dobra da oferta
