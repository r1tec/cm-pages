# Investigação: a equipe mexer nas páginas de venda sem tocar em código

Data: 21/11/2026. Somente leitura: nada foi alterado, publicado ou construído.
Projetos lidos: cm-pages (Contém Magia) e rp-pages (Rogeria Pinheiro).

## Em 5 linhas

1. Hoje todo texto, preço, link de compra e imagem de uma página mora dentro do arquivo da própria página; não existe painel, planilha nem tela do Raiz1 de onde a página leia conteúdo.
2. Uma mudança só vai ao ar quando alguém roda o publicador no Mac com a senha da hospedagem; subir para o GitHub não publica nada, e não existe link de prévia para a equipe ver antes.
3. Sem código, hoje dá para trocar só três coisas: o título e a descrição que aparecem no Google, o nome e o resumo da página na home, e uma imagem por outra com o mesmo nome.
4. Em dois meses e meio foram 80 mudanças de página: 21 eram conteúdo puro (texto, preço, foto, link), 11 eram página nova e 48 eram técnica; ou seja, a equipe resolveria sozinha cerca de um quarto, quase tudo em páginas de campanha.
5. Com 18 páginas de um lado e 1 do outro, um painel não se paga: a versão mínima é a equipe pedir a mudança em português a um assistente que edita numa cópia separada, você conferir a prévia e publicar. Preço e link de compra continuam passando por você.

---

## 1. Como uma página é feita

**Tudo fica no arquivo da página.** Cada pasta com `index.html` é uma rota (README.md:7-11). Não há banco, CMS nem Raiz1 alimentando o conteúdo: o motor só fala com a internet para limpar cache, medir velocidade, pesquisar palavras e avisar buscadores (limpar_cache.py:18, medir.py:85, scripts/palavras_chave.py:17, raiz.py:280).

| Item | Onde fica | Evidência |
|---|---|---|
| Texto visível | Dentro do `index.html` da página | drb/index.html:54 (corpo inteiro em poucas linhas gigantes) |
| Preço visível | Dentro do `index.html`, como texto | drb/index.html:54-60, fsa/index.html:379, 52e/index.html:246-264 (rp-pages) |
| Link de compra | Dentro do `index.html`, escrito em cada botão | drb/index.html:61, coe/index.html:393, 52e/index.html:265 (rp-pages) |
| Imagem | Arquivo em `<slug>/assets/` (páginas leves) ou embutida no próprio HTML (exportações do Claude Design) | bce/assets (18 imagens); coe/index.html:393 (uma linha de 3,8 MB) |
| Título e descrição do Google, imagem de compartilhamento, preço para o Google | Arquivo de conteúdo `<slug>/seo.json` | seo.py:1-12, drb/seo.json |
| Nome e resumo na home e no sitemap | Arquivo de conteúdo `config/raiz/paginas.json` | raiz.py:36-41 |
| Domínio, marca, endereço do checkout (só rp-pages) | `site.json` | rp-pages/config_site.py:1-15, rp-pages/site.json |
| Ajustes técnicos por página | `desempenho.json`, `rastreamento.json`, `reduzir.json`, `cores.json` | otimizar.py:341, rastreamento.py:31, otimizar.py:46, otimizar.py:860 |

**O preço está escrito em três lugares que ninguém sincroniza:** na página, no `seo.json` e no checkout do Raiz1 (tabela `checkout_offers`, coluna `price_cents`: raiz1-lovable/src/integrations/supabase/types.ts:3399). O motor só confere o `seo.json` contra a página (seo.py:83-90); página contra checkout é conferida no olho. Os commits "fsa: plano trimestral com o preço do checkout" (20/10) e "eba: parcela do Plano Anual igual ao checkout" (17/10) são correções desse descompasso.

**Três tipos de página, com dificuldade diferente para editar:**

| Tipo | Páginas | Como é o arquivo |
|---|---|---|
| HTML leve, escrito à mão | 10edb, bm26, bm26-vd, eba, link (cm) e 52e (rp) | Legível; maior linha abaixo de 1.100 caracteres |
| Migrada do WordPress | bce, bco, bpa, bpv, drb, gdp, mce, mpg, mpp | Marcação do Elementor em linhas de 11 mil a 30 mil caracteres |
| Exportação do Claude Design | coe, fsa, ecm-26 (e a variação antiga ecm-26-v1) | O texto vive dentro de um pacote, numa única linha de 2 a 3,8 MB; a fonte de verdade é o projeto no Claude Design |

O que vai ao ar não é o arquivo editado: o preparo pré-monta a página, tira todos os scripts e reinjeta só o do botão de compra, a animação e o contador (estatico.py:205-206, estatico.py:26, 58, 77).

## 2. Como publica

- **Quem dispara:** uma pessoa (ou o assistente dela) rodando `./publicar.sh <slug>` no Mac (publicar.sh:1-13). Na prática, o dono: dos 165 commits, 148 são dele e 16 do assistente.
- **Por onde:** FTP direto para a hospedagem, a partir da pasta local, e depois limpeza do cache da Cloudflare (publicar.sh:139-151). A senha fica num arquivo fora do Git (publicar.sh:34-41, .gitignore).
- **GitHub não publica.** É só espelho (.claude/CLAUDE.md:50). A publicação automática por push e a do cPanel foram desligadas de propósito porque subiam a página crua por cima da otimizada (.github/workflows/deploy-ftp.yml:3-8, .cpanel.yml, README.md:85-87). Não há Lovable nem Cloudflare Pages no caminho.
- **O que está no ar não é amarrado a um commit:** o publicador envia o que estiver na pasta local, commitado ou não. Já houve página no ar à frente do repositório (caso `coe`, .claude/CLAUDE.md:60-62).
- **Prévia por branch com link: não existe.** A prévia é uma pasta local no Mac (`python3 preparar.py <slug> --saida /tmp/preview-<slug>`, README.md:49-57). O trabalho é direto na `main` (CLAUDE.md:89).
- **Só o Mac prepara e publica:** o preparo procura o Chrome em caminhos de Mac e Linux (otimizar.py:27-34) e o envio usa uma ferramenta instalada pelo Homebrew (publicar.sh:92-100). No PC Windows do dono o fluxo já é "edita, envia para o GitHub, publica pelo Mac".
- **rp-pages:** mesmo publicador, outra hospedagem (rp-pages/publicar.sh:113-126, rp-pages/docs/HOSPEDAGEM.md:6-15). Não tem repositório remoto (rp-pages/.claude/CLAUDE.md:49-50) e a raiz do site é um WordPress no ar que não pode ser tocado (rp-pages/.claude/CLAUDE.md:42-45).

## 3. O que já dá para trocar sem código

| O quê | Como | Limite |
|---|---|---|
| Título e descrição no Google, imagem de compartilhamento | Editar `<slug>/seo.json`; ele vence o que estiver no HTML (seo.py:12) | Não muda nada visível na página. O preparo recusa título fora de 30–65 caracteres, descrição fora de 70–165 e preço que não aparece na página (seo.py:77-90) |
| Nome e resumo na home, /sobre e sitemap | Editar `config/raiz/paginas.json` (raiz.py:36-41) | Só a raiz do domínio; só cm-pages |
| Trocar uma imagem | Subir outra com o mesmo nome em `<slug>/assets/` | Só páginas leves e migradas; mesma proporção, senão o layout mexe. Nas exportações do Claude Design a imagem está dentro do pacote |
| Endereço do checkout do site inteiro (rp-pages) | `site.json` | Decisão do dono, não da equipe |

Fora isso, nada: não há painel, e o Raiz1 não tem tabela nem tela de página. Das 295 tabelas do Raiz1, as mais próximas são `checkout_offers` (preço real da oferta), `products_catalog`, `funnel_campaign` (campanhas e o formulário embutido na bm26: bm26/index.html:142, raiz1-lovable/src/lib/constants.ts:280) e os documentos de projeto; nenhuma guarda texto ou imagem de página, e nenhuma página lê delas. Em todos os casos acima a mudança ainda depende de alguém publicar.

## 4. Quanto do trabalho cairia em "conteúdo"

**Escala de hoje:** cm-pages tem 18 páginas (15 na home e no sitemap; ficam fora ecm-26, ecm-26-v1 e bm26-vd). rp-pages tem 1 página (52e).

**Contagem dos 80 commits de página de 01/09 a 21/11/2026** (commit não é pedido: um pedido pode virar vários commits e vice-versa):

| Tipo | Commits | Exemplos |
|---|---|---|
| Texto | 10 | "44 mil alunos em todas", "inscrições abertas até 09/10", tabela de bônus da bm26 |
| Preço | 4 | ecm-26 de 897 para 497, novo lote R$ 597, parcela da eba, plano da fsa |
| Imagem | 4 | fotos do Edu e da sessão de honra na ecm-26 |
| Link ou botão | 3 | botão da Black Magick na página de links, link do plano anual |
| **Conteúdo puro** | **21 (26%)** | |
| Página nova ou migração | 11 (14%) | bm26, bm26-vd, link, 10edb, eba, mpp, bco, bpa, bpv, ecm-26 |
| Técnica (velocidade, rastreamento, chat, SEO, formulário) | 48 (60%) | |

Leitura por tarefa típica:

- **Trocar texto:** seria conteúdo. Ressalva: 3 dos 10 casos mudaram a estrutura (lista virou tabela, seção nova), o que nenhum campo de texto cobre.
- **Trocar imagem:** já é quase conteúdo nas 15 páginas que guardam imagem em arquivo; não é nas 3 exportações do Claude Design.
- **Trocar preço:** é conteúdo na página, mas a verdade está no checkout. Mexer só na página cria a divergência que já precisou ser corrigida duas vezes.
- **Trocar link de compra:** é conteúdo, mas é o que decide se a cliente consegue pagar. Fica com o dono.
- **Criar página a partir de modelo:** hoje é 0% conteúdo. Não existe modelo: cada página nasce de uma exportação do Claude Design ou de uma migração feita à mão (.claude/skills/preparar-pagina/SKILL.md:3 e :17, docs/RECEITA-PAGINAS.md:30-36). O que há em comum são regras de design (`_padroes/`), não uma página-base.

O volume de conteúdo se concentra em páginas de campanha (ecm-26 e bm26 somam 12 dos 21). As 9 páginas migradas do WordPress quase não mudam de texto.

## 5. Versão mínima

### Primeiro: o que funciona com zero peça nova

O dono já trabalha assim no PC Windows desde 08/10: pede a mudança em português ao assistente, que edita, envia ao GitHub, e a publicação sai pelo Mac. As regras que protegem checkout, rastreamento e texto aprovado já estão escritas no repositório e o assistente as segue (CLAUDE.md:37-39). O README já prevê outra pessoa da equipe na máquina dela (README.md:89-96). E a trava de publicação já existe sozinha: sem a senha da hospedagem, ninguém publica (publicar.sh:34-40).

### Proposta ao dono

- **Como é hoje / por que não atende:** toda mudança, até uma data, passa pelas mãos do dono do pedido à publicação. A equipe não tem como preparar nada sozinha nem como ver o resultado antes.
- **Como fica depois:** a pessoa da equipe descreve a mudança em português ("troca a data para 12/12", "usa esta foto no topo"). O assistente faz a alteração numa cópia separada, que não afeta o site. O dono recebe a prévia, confere e publica. Mudança de preço ou de link de compra vem marcada e só segue com o sim dele.
- **Como chegamos lá:** dar à equipe acesso ao repositório para trabalhar em cópia separada (branch), nunca na principal; escrever nas regras do repositório que quem não é o dono não publica nem mexe em preço, link de compra ou rastreamento sem aprovação; e ter um endereço de prévia para o dono conferir sem montar nada à mão.
- **O que muda na tela:** nada no site. A equipe passa a usar o assistente; o dono passa a receber prévias para aprovar.
- **Efeitos colaterais:** a equipe ganha acesso de escrita ao repositório (o histórico protege, mas é acesso novo). Duas pessoas na mesma página ao mesmo tempo geram conflito, que o dono resolve ao juntar. Prévia em endereço público dispara os pixels se não for isolada. No rp-pages não há repositório remoto, então lá o caminho nem começa sem criar um.
- **Custo:** baixo. Uma regra escrita e acessos; uma peça nova pequena (a prévia com link).

### Peças novas, cada uma com o candidato existente

**Peça 1 — Regra "equipe trabalha em cópia separada e não publica".**
- Candidato existente: regra de Git do motor (CLAUDE.md:89, "trabalho direto na main") e a do site (.claude/CLAUDE.md:73-76) — não serve porque manda todo mundo direto para a principal e autoriza enviar sem pedir; foi escrita para um dono só.
- Escala de hoje: 1 pessoa publica; equipe de tamanho não informado.
- Versão mínima: um parágrafo nas regras do site, sem código.

**Peça 2 — Prévia com link para aprovar.**
- Candidato existente A: `preparar.py --saida` (README.md:49-57) — não serve porque gera uma pasta no Mac, sem endereço que outra pessoa abra.
- Candidato existente B: a pasta de destino do publicador é configurável (publicar.sh:44 e :137), então o mesmo comando poderia mandar a página para uma pasta de prévia no próprio domínio — não serve como está porque a prévia sairia com os pixels ligados, o espelho e a limpeza de cache seguiriam o endereço real (publicar.sh:145-150), e o buscador poderia indexar. Não testado.
- Candidato existente C: a publicação automática por push (.github/workflows/deploy-ftp.yml) — não serve porque sobe a página crua, direto na produção, e foi desligada por isso.
- Escala de hoje: cerca de 2 mudanças de conteúdo por semana.
- Versão mínima: estender o candidato B com um modo de prévia (pasta fora do sitemap, sem pixel, sem indexação), rodado pelo dono no Mac.

**Peça 3 (só se o volume crescer) — arquivo de conteúdo visível por página.**
- Candidato existente A: `seo.json` (seo.py:144-187) — não serve porque só alcança o cabeçalho invisível; o padrão dele ("o arquivo vence o HTML", com conferência antes de publicar) é o que se estenderia.
- Candidato existente B: `cores.json` (otimizar.py:858-872), que já é uma lista "troque isto por aquilo" aplicada no preparo — não serve porque só roda nas exportações do Claude Design e foi feito para cor; para texto, troca por coincidência é frágil (a mesma frase pode aparecer duas vezes).
- Candidato existente C: tabela no Raiz1 (`checkout_offers`, `funnel_campaign`) — não serve porque nenhuma guarda texto de página e o site é estático: precisaria de tela nova, permissão nova e de o preparo passar a ler o banco, para 19 páginas.
- Escala de hoje: 21 mudanças de conteúdo em 11 semanas, 12 delas em duas páginas de campanha.
- Versão mínima: campos só para o que muda sempre em campanha (data, preço exibido, lote, texto do botão) e só nas páginas leves. Não recomendado agora.

**Peça 4 (só se criar página virar rotina da equipe) — página-modelo.**
- Candidato existente: as páginas leves mais recentes (10edb, bm26-vd) e os padrões de `_padroes/` — não servem porque cada uma tem desenho próprio e não foi feita para ser copiada; `_padroes/` tem regras, não uma página.
- Escala de hoje: 11 páginas novas em 11 semanas, todas com design próprio.
- Versão mínima: não recomendado agora; página nova continua com o dono.

### O que fica sempre com o dono

- Publicar (cm-pages e rp-pages).
- Link de compra e preço: a página só muda junto com o checkout, com o sim dele.
- Rastreamento, pixels e GTM.
- Páginas exportadas do Claude Design (coe, fsa, ecm-26): a mudança de texto se faz no Claude Design ou pelo assistente com conferência redobrada, não por edição direta.

## Limites desta investigação

- O Raiz1 foi lido pelo código local (raiz1-lovable, estado de 19/11/2026), não pelo banco em produção.
- Não conferi quem tem acesso ao repositório no GitHub nem se há proteção da branch principal.
- O tamanho da equipe e quais ferramentas ela já usa não estavam nos repositórios.
- O candidato B da prévia (pasta de destino configurável) foi lido, não executado.
- A classificação dos commits foi feita pela descrição de cada um, sem abrir os diffs.
