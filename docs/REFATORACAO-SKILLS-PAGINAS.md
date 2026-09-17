# Separação de preparar, otimizar e publicar — 12/09/2026

Implementada a divisão aprovada pelo dono. Ajustes pequenos não iniciam uma
auditoria geral; PageSpeed deixou de ser requisito de toda publicação.
Nenhuma página foi publicada nem alterada nesta tarefa de infraestrutura.

## Entradas

| Pedido | Fluxo |
| --- | --- |
| “Publique a versão que vi no preview” | `publicar`: confere o build escolhido, envia e limpa cache |
| “Troque o ícone e publique” | Ajuste/teste do componente → build → envio; sem PageSpeed automático |
| “O chat está atrasando a página” | `otimizar`: diagnóstico delimitado, comparação pertinente |
| “Otimize tudo para máxima performance” | `otimizar`: audits completos e ganhos demonstráveis, sem loop para perseguir 100 |
| “Recebi uma página do Claude Design” | `preparar-pagina`: conversão, fidelidade, funções, otimização e preview |
| “Só quero preview” | Preparação local; não publica |

Fontes canônicas: `.claude/skills/{publicar,otimizar,preparar-pagina}/`.
Links em `.agents/skills/` expõem as mesmas fontes ao Codex. As receitas técnicas
foram preservadas em `otimizar/REFERENCIA-TECNICA.md`; a referência antiga de
publicação contém apenas o encaminhamento para a nova divisão. `CLAUDE.md`,
`README.md` e os padrões de design foram alinhados ao novo escopo.

## Programa

- `preparar.py`: preparação sem FTP ou PageSpeed. Manifesto fora do diretório
  público, com hashes da fonte, configuração, código de transformação e saída.
  Construção em pasta temporária e preservação da versão anterior em caso de falha.
- `--reusar`: verifica integridade/correspondência; só reconstrói se necessário.
- `--conferir`: análise visual opcional; devolve avisos e falhas ao chamador.
- `publicar.sh --build <pasta> <slug>`: exige build íntegro/atual; não reconstrói
  um preview escolhido silenciosamente. Envia uma cópia conferida e isolada.
- `publicar.sh <slug>`: reutiliza o build padrão ou prepara uma vez quando necessário.
  Não chama `verificar.py` ou `medir.py` automaticamente.
- Cache de recompressão WebP no ramo HTML/WordPress, baseado nos bytes da fonte,
  opções e codificadores. Cache corrompido é ignorado e regenerado. Resultado
  sempre deriva do original, sem perda acumulada por recompressões sucessivas.
- Modos existentes de GTM, limpeza e espelhamento foram preservados, assim como
  as edições locais preexistentes nesses trechos. Destinos/configurações não mudaram.

O manifesto não significa aprovação visual. A sessão mantém as provas pertinentes
do preview. Builds legados sem manifesto precisam ser preparados uma vez pelo novo
comando. O modo legado sem slugs ainda publica todas; usar slugs explícitas em
pedidos pontuais. Credenciais não entram em manifestos ou snapshots.

## Validação

`PYTHONDONTWRITEBYTECODE=1 python3 scripts/testar-publicacao.py`: **14 testes aprovados**.
Cobertura: reuso sem compilar/conferir, alterações na fonte/assets/pipeline,
manifesto inválido, build adulterado/incompleto, falha/race de preparação,
snapshot imutável, proteção da fonte/caminhos, status do verificador opcional,
cache de imagens, preview explícito e ajuda sem credenciais.

Testes do publicador usam uma árvore temporária, credenciais fictícias e um
`lftp` substituto que só copia arquivos locais. Comprovaram preparo único em dois
envios e bloqueio antes de enviar uma versão não correspondente. Não usaram FTP
real, Cloudflare ou PageSpeed. Sintaxe Bash e diff conferidos.

As três skills passaram no `quick_validate.py` oficial. PyYAML foi instalado apenas
no ambiente isolado `.build/skills-split/venv`, sem modificar o Python global.
Links Markdown locais verificados; nenhuma referência quebrada.

Medições locais com a MCE durante a alteração:

| Operação de preparação | Tempo |
| --- | --- |
| Primeira preparação | 14,61 s |
| Nova preparação com cache de imagens | 6,78 s |
| Reuso do build pronto | 0,15 s |

Os 25 arquivos dos dois builds reais ficaram idênticos byte por byte entre si e
ao último build publicado da MCE. O segundo preparo reutilizou 12 imagens sem
recodificar. São tempos locais de preparação, não duração de FTP ou garantia para
outras páginas. O cache novo de imagens cobre WebP de HTML/WordPress; o reuso do
build completo atende também exportações bundler.

Evidências completas em `.build/skills-split/` (ignorado). Tempo total de execução
e consumo de tokens não instrumentados; nenhum subagente utilizado. Alterações
desta refatoração permanecem no workspace; não houve commit/push ou publicação
de sites nesta tarefa. A mudança de infraestrutura não autoriza publicar páginas.
