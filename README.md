# Contém Magia Pages

**Para publicar uma página:** `./publicar.sh <slug>` (ou skill `publicar`).
**Para preparar uma página nova:** skill `preparar-pagina`.
**Para melhorar desempenho:** skill `otimizar`.

Páginas de venda estáticas da Escola Contém Magia. Cada pasta da raiz é uma rota:

```
coe/index.html   ->  https://contemmagia.com.br/coe
```

Há HTML direto, páginas migradas de WordPress e exportações do Claude Design.
`preparar.py` produz a versão de entrega sem alterar o original, guarda os hashes
da fonte/build e reutiliza imagens já recomprimidas. A preparação técnica não é
uma auditoria completa de desempenho.

## Fluxo de uma página nova

1. **Copy travada** — texto aprovado antes do design começar.
2. **Design no Claude Design** — layout, cor, imagem, fonte. As três regras de
   `_padroes/checklist-design.md` valem aqui: contraste 4,5, no máximo 4 pesos
   de fonte, imagem no dobro do tamanho exibido.
3. **Preparação e preview** — `python3 preparar.py <slug>`, com verificações
   proporcionais ao trabalho. Página nova usa o fluxo completo da sua skill.
4. **Publicação** — `./publicar.sh <slug>` envia o build atual; se ainda não
   existir, prepara uma vez. Não roda PageSpeed nem conferência visual por padrão.
5. **Commit e push** — o GitHub é o espelho, a hospedagem é o resultado.

## Publicar

```
./publicar.sh          # todas as páginas
./publicar.sh coe      # só a slug coe
./publicar.sh --build /tmp/preview-mce mce  # exatamente o preview preparado
```

Use slugs explícitas em pedidos pontuais. Sem argumentos, o modo legado continua
publicando todas. `--build` aceita uma slug e exige um build íntegro que corresponda
à fonte/configuração/pipeline atuais: se algo mudou, falha antes do envio, sem
reconstruir o preview escolhido. O publicador envia uma cópia conferida para evitar
que outro build altere os arquivos durante a transferência.

O fluxo comum reutiliza `.build/<slug>` quando atual. Caso precise preparar,
reaproveita a recompressão de WebP das páginas HTML/WordPress pelo cache;
imagens inalteradas não precisam passar novamente pelos codificadores.
O cache e os manifestos ficam fora da pasta enviada ao servidor.

## Preparar sem publicar

```sh
python3 preparar.py mce                             # novo build em .build/mce
python3 preparar.py mce --saida /tmp/preview-mce     # build para preview
python3 preparar.py mce --reusar                     # reutiliza se íntegro/atual
python3 preparar.py mce --conferir                   # adiciona imagens/contraste
python3 preparar.py mce --verificar-build            # só confere hashes
```

Para uma pasta de preview, escolha uma saída nova ou já gerenciada por esse
comando. Builds antigos feitos diretamente com `otimizar.py` não têm manifesto;
prepare uma vez pelo novo comando. Não edite o HTML do build à mão: altere a fonte
e prepare novamente. Falha de preparação preserva o build anterior; o manifesto
prova integridade/correspondência, não fidelidade visual ou aprovação do usuário.

Uma troca de ícone pede conferir seus estados. Layout pede conferir as regiões e
larguras afetadas. Checkout/pixels pedem testar esses fluxos. PageSpeed entra por
pedido de desempenho ou impacto concreto em carregamento, não em toda publicação.
Reutilize verificações da mesma versão em vez de repetir a sequência inteira.

## Otimização quando solicitada

`python3 medir.py <slug> --both --tentativas 1 --output /tmp/psi-<slug>.json`
mede a página pública, sem publicar. A skill `otimizar` trata diagnóstico e
melhorias. `afinar.sh` continua sendo o auxiliar legado que publica e mede em
rodadas limitadas; só use quando essas publicações estiverem autorizadas.

**Este é o único caminho de publicação.** O workflow do GitHub Actions e o
`.cpanel.yml` foram desativados: subiam o arquivo cru, sem otimizar e sem
limpar o cache, por cima do resultado do `publicar.sh`.

## Máquina nova / outra pessoa da equipe

```
git clone https://github.com/r1tec/cm-pages.git
cd cm-pages
cp .env.example .env      # preencher FTP_SENHA e CF_API_TOKEN
./publicar.sh <slug>
```

As três skills vêm com o projeto, em `.claude/skills/`; `.agents/skills/` aponta
para essas mesmas fontes, sem cópias concorrentes.
Requisitos na máquina: `python3`, `lftp` (instalado automaticamente via
Homebrew) e Google Chrome (usado para pré-montar a página e para medir peso e
contraste).

## Estrutura

```
_padroes/              regras de design compartilhadas por todas as páginas
.claude/skills/        publicar, otimizar e preparar-pagina
<slug>/index.html      a página, exportada do Claude Design
<slug>/REGRAS.md       regras de conteúdo daquela página
<slug>/reduzir.json    remendo local: encolher imagens (evite; corrija no Design)
<slug>/cores.json      remendo local: trocar cores por contraste (idem)
preparar.py            build local, manifesto e reuso
otimizar.py            conversão técnica, imagens e fontes (usado pelo preparador)
estatico.py            pré-monta a página sem React
verificar.py           confere imagem e contraste, só avisa
publicar.sh            envio de build, espelho configurado e cache
```
